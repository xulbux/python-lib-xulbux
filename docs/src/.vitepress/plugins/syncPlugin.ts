import { exec } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

function executePythonCommand(
  cwd: string,
  args: string[],
  successMsg: string,
  filePath: string,
  onSuccess?: () => void
) {
  function run(commands: string[]) {
    exec(`${commands[0]} ${args.join(' ')}`, { cwd }, (err, _stdout, stderr) => {
      if (err) {
        if (commands.length > 1) {
          run(commands.slice(1));
        } else {
          // oxlint-disable-next-line no-console
          console.error(err, stderr);
        }
      } else {
        // oxlint-disable-next-line no-console
        console.log(`[sync] ${successMsg}: ${path.basename(filePath)}`);
        onSuccess?.();
      }
    });
  }
  run(['python', 'python3', 'py']);
}

export function syncPlugin(dirname: string) {
  return {
    configureServer(server: {
      watcher: {
        add: (path: string) => void;
        on: (event: string, cb: (eventName: string, filePath: string) => void) => void;
      };
      restart: () => void;
    }) {
      const rootDir = path.resolve(dirname, '../../..');
      const srcDir = path.resolve(dirname, '../../src');
      const pySrcDir = path.resolve(dirname, '../../../src');
      const changelogPath = path.resolve(dirname, '../../../CHANGELOG.md');

      server.watcher.add(srcDir);
      server.watcher.add(pySrcDir);
      server.watcher.add(changelogPath);

      function runPythonCommand(
        args: string[],
        successMsg: string,
        filePath: string,
        restartServer = false
      ) {
        executePythonCommand(
          rootDir,
          args,
          successMsg,
          filePath,
          restartServer ? () => server.restart() : undefined
        );
      }

      function handleDocsSrc(eventName: string, filePath: string) {
        const dest = filePath.replace(srcDir, path.resolve(dirname, '../'));
        if (eventName === 'add' || eventName === 'change') {
          fs.mkdirSync(path.dirname(dest), { recursive: true });
          if (filePath.endsWith('.md')) {
            runPythonCommand(
              ['docs/build.py', '--process-file', `"${filePath}"`],
              'Processed MD',
              filePath
            );
          } else {
            fs.copyFileSync(filePath, dest);
            if (filePath.endsWith('sidebar.json')) {
              runPythonCommand(
                ['docs/build.py'],
                'Rebuilt docs due to sidebar.json change',
                filePath,
                true
              );
            }
          }
        } else if (eventName === 'unlink') {
          if (fs.existsSync(dest)) {
            fs.unlinkSync(dest);
          }
          if (filePath.endsWith('sidebar.json')) {
            runPythonCommand(
              ['docs/build.py'],
              'Rebuilt docs due to sidebar.json unlink',
              filePath,
              true
            );
          } else if (filePath.endsWith('.md')) {
            runPythonCommand(['docs/build.py'], 'Rebuilt docs due to MD unlink', filePath, true);
          }
        }
      }

      function handlePySrc(eventName: string, filePath: string) {
        const relPyPath = path.relative(pySrcDir, filePath);
        const parts = relPyPath.split(path.sep);
        if (
          parts.length >= 2 &&
          parts[0] === 'xulbux' &&
          !parts[parts.length - 1].startsWith('_')
        ) {
          if (eventName === 'change') {
            runPythonCommand(
              ['docs/build.py', '--process-file', `"${filePath}"`],
              'Processed Python API',
              filePath
            );
          } else if (eventName === 'add' || eventName === 'unlink') {
            runPythonCommand(
              ['docs/build.py'],
              `Rebuilt docs due to Python source ${eventName}`,
              filePath,
              true
            );
          }
        }
      }

      server.watcher.on('all', (eventName: string, filePath: string) => {
        if (filePath === changelogPath) {
          if (eventName === 'change' || eventName === 'add') {
            runPythonCommand(
              ['docs/build.py', '--process-file', `"${filePath}"`],
              'Processed Changelog',
              filePath
            );
          }
        } else if (filePath.startsWith(srcDir)) {
          handleDocsSrc(eventName, filePath);
        } else if (filePath.startsWith(pySrcDir) && filePath.endsWith('.py')) {
          handlePySrc(eventName, filePath);
        }
      });
    },
    name: 'sync-docs-src',
  };
}
