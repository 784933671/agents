# Node.js 基础

## 文件系统（fs/promises）

```javascript
import { readFile, writeFile, appendFile, mkdir, rm, readdir, stat } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';

// 读取文件
const content = await readFile('./file.txt', 'utf-8');

// 写入文件（覆盖）
await writeFile('./output.txt', 'Hello World');

// 追加到文件
await appendFile('./log.txt', 'New log entry\n');

// 读取 JSON 文件
const readJSON = async (path) => {
  const content = await readFile(path, 'utf-8');
  return JSON.parse(content);
};

// 写入 JSON 文件
const writeJSON = async (path, data) => {
  await writeFile(path, JSON.stringify(data, null, 2));
};

// 创建目录（递归）
await mkdir('./nested/path/dir', { recursive: true });

// 删除目录/文件（递归）
await rm('./temp', { recursive: true, force: true });

// 列出目录
const files = await readdir('./src');
const filesWithTypes = await readdir('./src', { withFileTypes: true });

for (const file of filesWithTypes) {
  if (file.isDirectory()) {
    console.log(`[DIR] ${file.name}`);
  } else {
    console.log(`[FILE] ${file.name}`);
  }
}

// 获取文件状态
const stats = await stat('./file.txt');
console.log('Size:', stats.size);
console.log('Modified:', stats.mtime);
console.log('Is file:', stats.isFile());

// 检查是否存在（仅同步）
if (existsSync('./path')) {
  // 路径存在
}
```

## Path 模块

```javascript
import { join, resolve, dirname, basename, extname, parse, format } from 'path';
import { fileURLToPath } from 'url';

// 在 ESM 中获取当前文件和目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 拼接路径（跨平台）
const filePath = join(__dirname, 'data', 'config.json');

// 解析为绝对路径
const absolutePath = resolve('./relative/path');

// 获取文件名
const filename = basename('/path/to/file.txt'); // 'file.txt'
const filenameNoExt = basename('/path/to/file.txt', '.txt'); // 'file'

// 获取扩展名
const ext = extname('file.txt'); // '.txt'

// 解析路径
const parsed = parse('/home/user/file.txt');
// {
//   root: '/',
//   dir: '/home/user',
//   base: 'file.txt',
//   ext: '.txt',
//   name: 'file'
// }

// 格式化路径
const formatted = format({
  dir: '/home/user',
  base: 'file.txt'
}); // '/home/user/file.txt'
```

## 流

```javascript
import { createReadStream, createWriteStream } from 'fs';
import { pipeline } from 'stream/promises';
import { Transform } from 'stream';

// 高效读取大文件
const readStream = createReadStream('./large-file.txt', {
  encoding: 'utf-8',
  highWaterMark: 16 * 1024 // 16KB 分块
});

readStream.on('data', (chunk) => {
  console.log('Chunk:', chunk);
});

readStream.on('end', () => {
  console.log('Finished reading');
});

readStream.on('error', (error) => {
  console.error('Error:', error);
});

// 写入流
const writeStream = createWriteStream('./output.txt');
writeStream.write('Line 1\n');
writeStream.write('Line 2\n');
writeStream.end('Final line\n');

// 管道连接流
const input = createReadStream('./input.txt');
const output = createWriteStream('./output.txt');
input.pipe(output);

// 转换流
const upperCaseTransform = new Transform({
  transform(chunk, encoding, callback) {
    const transformed = chunk.toString().toUpperCase();
    callback(null, transformed);
  }
});

await pipeline(
  createReadStream('./input.txt'),
  upperCaseTransform,
  createWriteStream('./output.txt')
);

// 异步迭代流
const processStream = async (filePath) => {
  const stream = createReadStream(filePath, { encoding: 'utf-8' });

  for await (const chunk of stream) {
    processChunk(chunk);
  }
};
```

## EventEmitter

```javascript
import { EventEmitter } from 'events';

class DataProcessor extends EventEmitter {
  async process(data) {
    this.emit('start', { itemCount: data.length });

    for (let i = 0; i < data.length; i++) {
      await this.processItem(data[i]);
      this.emit('progress', { current: i + 1, total: data.length });
    }

    this.emit('complete', { processed: data.length });
  }

  async processItem(item) {
    // 处理逻辑
    if (item.error) {
      this.emit('error', new Error('Item processing failed'));
    }
  }
}

// 使用方式
const processor = new DataProcessor();

processor.on('start', ({ itemCount }) => {
  console.log(`Starting processing ${itemCount} items`);
});

processor.on('progress', ({ current, total }) => {
  console.log(`Progress: ${current}/${total}`);
});

processor.on('complete', ({ processed }) => {
  console.log(`Completed: ${processed} items`);
});

processor.on('error', (error) => {
  console.error('Processing error:', error);
});

// 一次性监听器
processor.once('complete', () => {
  console.log('First completion');
});

// 移除监听器
const handler = () => console.log('Event fired');
processor.on('event', handler);
processor.off('event', handler);
```

## 子进程

```javascript
import { spawn, exec, execFile } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// 执行 shell 命令
const { stdout, stderr } = await execAsync('ls -la');
console.log('Output:', stdout);

// 创建带流式输出的进程
const ls = spawn('ls', ['-la', '/usr']);

ls.stdout.on('data', (data) => {
  console.log(`stdout: ${data}`);
});

ls.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

ls.on('close', (code) => {
  console.log(`Process exited with code ${code}`);
});

// 执行 Node.js 脚本
const child = spawn('node', ['script.js'], {
  cwd: './scripts',
  env: { ...process.env, CUSTOM_VAR: 'value' }
});
```

## Worker Threads

```javascript
import { Worker, isMainThread, parentPort, workerData } from 'worker_threads';

if (isMainThread) {
  // 主线程
  const worker = new Worker(new URL(import.meta.url), {
    workerData: { items: [1, 2, 3, 4, 5] }
  });

  worker.on('message', (result) => {
    console.log('Result from worker:', result);
  });

  worker.on('error', (error) => {
    console.error('Worker error:', error);
  });

  worker.on('exit', (code) => {
    console.log(`Worker exited with code ${code}`);
  });

  worker.postMessage({ command: 'process' });
} else {
  // Worker 线程
  const { items } = workerData;

  parentPort.on('message', (message) => {
    if (message.command === 'process') {
      const result = items.reduce((sum, n) => sum + n, 0);
      parentPort.postMessage(result);
    }
  });
}

// Worker 池模式
class WorkerPool {
  #workers = [];
  #queue = [];

  constructor(workerPath, poolSize = 4) {
    for (let i = 0; i < poolSize; i++) {
      this.#workers.push({
        worker: new Worker(workerPath),
        busy: false
      });
    }
  }

  async execute(data) {
    return new Promise((resolve, reject) => {
      const task = { data, resolve, reject };
      this.#queue.push(task);
      this.#processQueue();
    });
  }

  #processQueue() {
    const availableWorker = this.#workers.find(w => !w.busy);
    if (!availableWorker || this.#queue.length === 0) return;

    const task = this.#queue.shift();
    availableWorker.busy = true;

    const handleMessage = (result) => {
      task.resolve(result);
      availableWorker.busy = false;
      availableWorker.worker.off('message', handleMessage);
      this.#processQueue();
    };

    availableWorker.worker.on('message', handleMessage);
    availableWorker.worker.postMessage(task.data);
  }
}
```

## 进程与环境

```javascript
// 环境变量
const port = process.env.PORT || 3000;
const isDev = process.env.NODE_ENV === 'development';

// 命令行参数
const args = process.argv.slice(2);
console.log('Arguments:', args);

// 退出进程
process.exit(0); // 成功
process.exit(1); // 错误

// 优雅关闭
process.on('SIGINT', async () => {
  console.log('Shutting down gracefully...');
  await cleanup();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('Received SIGTERM');
  await cleanup();
  process.exit(0);
});

// 未处理错误
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection:', reason);
  process.exit(1);
});

// 进程信息
console.log('PID:', process.pid);
console.log('Platform:', process.platform);
console.log('Node version:', process.version);
console.log('Memory usage:', process.memoryUsage());
console.log('Uptime:', process.uptime());
```

## HTTP/HTTPS 服务器

```javascript
import { createServer } from 'http';
import { readFile } from 'fs/promises';

const server = createServer(async (req, res) => {
  // 解析 URL 和方法
  const { url, method } = req;

  // 设置 CORS 头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  // 路由处理
  if (url === '/api/users' && method === 'GET') {
    const users = [{ id: 1, name: 'John' }];
    res.writeHead(200);
    res.end(JSON.stringify(users));
  } else if (url === '/api/users' && method === 'POST') {
    let body = '';

    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', () => {
      const user = JSON.parse(body);
      res.writeHead(201);
      res.end(JSON.stringify({ id: 2, ...user }));
    });
  } else {
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));
  }
});

server.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});

// 优雅关闭
const shutdown = () => {
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
};

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
```

## 多核 Cluster

```javascript
import cluster from 'cluster';
import { cpus } from 'os';
import { createServer } from 'http';

const numCPUs = cpus().length;

if (cluster.isPrimary) {
  console.log(`Primary ${process.pid} is running`);

  // fork worker
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died`);
    cluster.fork(); // 重启 worker
  });
} else {
  // Worker 共享 TCP 连接
  const server = createServer((req, res) => {
    res.writeHead(200);
    res.end(`Handled by worker ${process.pid}\n`);
  });

  server.listen(3000);
  console.log(`Worker ${process.pid} started`);
}
```

## 快速参考

| 模块 | 使用场景 | 导入 |
|--------|----------|--------|
| `fs/promises` | 异步文件操作 | `import { readFile } from 'fs/promises'` |
| `path` | 路径处理 | `import { join } from 'path'` |
| `stream` | 流处理 | `import { pipeline } from 'stream/promises'` |
| `events` | 事件发射器 | `import { EventEmitter } from 'events'` |
| `child_process` | 创建进程 | `import { spawn } from 'child_process'` |
| `worker_threads` | 多线程 | `import { Worker } from 'worker_threads'` |
| `http` | HTTP 服务器 | `import { createServer } from 'http'` |
| `cluster` | 多核扩展 | `import cluster from 'cluster'` |
