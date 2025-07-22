const { spawn } = require('child_process');

const python = spawn('python', ['TrieternalX.py']);

python.stdout.on('data', (data) => {
    console.log(`Output dari Python: ${data}`);
});

python.stderr.on('data', (data) => {
    console.error(`Error dari Python: ${data}`);
});
