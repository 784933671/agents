# 浏览器 API

## Fetch API

```javascript
// 基础 GET 请求
const response = await fetch('/api/users');
const data = await response.json();

// 使用 JSON 发起 POST 请求
const response = await fetch('/api/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ name: 'John', email: 'john@example.com' })
});

// 错误处理
const fetchWithErrorHandling = async (url) => {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError') {
      console.error('Network error or CORS issue');
    }
    throw error;
  }
};

// 中止请求
const controller = new AbortController();
setTimeout(() => controller.abort(), 5000);

const response = await fetch('/api/data', {
  signal: controller.signal
});

// 文件上传
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  return fetch('/api/upload', {
    method: 'POST',
    body: formData,
  });
};
```

## Web Workers

```javascript
// main.js：创建 worker 并通信
const worker = new Worker('/worker.js');

worker.postMessage({ command: 'process', data: largeArray });

worker.onmessage = (event) => {
  console.log('Result from worker:', event.data);
};

worker.onerror = (error) => {
  console.error('Worker error:', error.message);
};

// 完成后终止
worker.terminate();

// worker.js：Worker 代码
self.onmessage = (event) => {
  const { command, data } = event.data;

  if (command === 'process') {
    const result = processLargeData(data);
    self.postMessage(result);
  }
};

function processLargeData(data) {
  // CPU 密集型工作
  return data.map(x => x * 2).reduce((a, b) => a + b, 0);
}

// Shared Worker（标签页之间共享）
const sharedWorker = new SharedWorker('/shared-worker.js');

sharedWorker.port.onmessage = (event) => {
  console.log('Shared worker message:', event.data);
};

sharedWorker.port.postMessage({ type: 'init' });
```

## Service Workers 与 PWA

```javascript
// 注册 Service Worker
if ('serviceWorker' in navigator) {
  const registration = await navigator.serviceWorker.register('/sw.js');
  console.log('SW registered:', registration);

  // 更新 Service Worker
  registration.addEventListener('updatefound', () => {
    const newWorker = registration.installing;
    newWorker.addEventListener('statechange', () => {
      if (newWorker.state === 'activated') {
        window.location.reload();
      }
    });
  });
}

// sw.js：Service Worker
const CACHE_NAME = 'v1';
const urlsToCache = ['/index.html', '/styles.css', '/app.js'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      // 命中缓存：返回响应
      if (response) {
        return response;
      }

      // 克隆请求
      const fetchRequest = event.request.clone();

      return fetch(fetchRequest).then((response) => {
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }

        const responseToCache = response.clone();

        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });

        return response;
      });
    })
  );
});

// 后台同步
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages());
  }
});
```

## Local Storage 与 IndexedDB

```javascript
// LocalStorage（同步，最大 5-10MB）
localStorage.setItem('theme', 'dark');
const theme = localStorage.getItem('theme');
localStorage.removeItem('theme');
localStorage.clear();

// SessionStorage（每个标签页独立）
sessionStorage.setItem('token', 'abc123');

// IndexedDB（异步，更大容量存储）
const openDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('myDatabase', 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      const objectStore = db.createObjectStore('users', { keyPath: 'id' });
      objectStore.createIndex('email', 'email', { unique: true });
    };
  });
};

const addUser = async (user) => {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['users'], 'readwrite');
    const objectStore = transaction.objectStore('users');
    const request = objectStore.add(user);

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

const getUser = async (id) => {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['users']);
    const objectStore = transaction.objectStore('users');
    const request = objectStore.get(id);

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};
```

## Intersection Observer

```javascript
// 图片懒加载
const imageObserver = new IntersectionObserver(
  (entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.add('loaded');
        observer.unobserve(img);
      }
    });
  },
  {
    root: null, // 视口
    rootMargin: '50px',
    threshold: 0.1
  }
);

document.querySelectorAll('img[data-src]').forEach((img) => {
  imageObserver.observe(img);
});

// 无限滚动
const loadMoreObserver = new IntersectionObserver(
  (entries) => {
    const lastEntry = entries[0];
    if (lastEntry.isIntersecting) {
      loadMoreItems();
    }
  },
  { threshold: 1.0 }
);

const sentinel = document.querySelector('#load-more-sentinel');
loadMoreObserver.observe(sentinel);
```

## Mutation Observer

```javascript
// 监听 DOM 变化
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === 'childList') {
      console.log('Nodes added/removed:', mutation.addedNodes, mutation.removedNodes);
    } else if (mutation.type === 'attributes') {
      console.log('Attribute changed:', mutation.attributeName);
    }
  });
});

observer.observe(document.body, {
  childList: true,
  attributes: true,
  subtree: true,
  attributeOldValue: true
});

// 完成后断开连接
observer.disconnect();
```

## Web 通知

```javascript
// 请求权限
const permission = await Notification.requestPermission();

if (permission === 'granted') {
  new Notification('Hello!', {
    body: 'This is a notification',
    icon: '/icon.png',
    tag: 'unique-tag',
    requireInteraction: false
  });
}

// Service Worker 通知
// sw.js
self.addEventListener('push', (event) => {
  const data = event.data.json();

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon,
      badge: '/badge.png',
      data: data.url
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data)
  );
});
```

## Canvas 与 WebGL

```javascript
// Canvas 2D
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

// 绘制矩形
ctx.fillStyle = '#FF0000';
ctx.fillRect(10, 10, 100, 100);

// 绘制文本
ctx.font = '30px Arial';
ctx.fillText('Hello Canvas', 10, 50);

// 绘制图片
const img = new Image();
img.onload = () => {
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
};
img.src = '/image.png';

// WebGL 基础设置
const gl = canvas.getContext('webgl2');

if (!gl) {
  console.error('WebGL2 not supported');
}

// 清空画布
gl.clearColor(0.0, 0.0, 0.0, 1.0);
gl.clear(gl.COLOR_BUFFER_BIT);
```

## Performance API

```javascript
// 性能计时
const timing = performance.timing;
const loadTime = timing.loadEventEnd - timing.navigationStart;
console.log('Page load time:', loadTime);

// Performance Observer
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log(`${entry.name}: ${entry.duration}ms`);
  }
});

observer.observe({ entryTypes: ['measure', 'navigation', 'resource'] });

// 自定义标记与测量
performance.mark('start-fetch');
await fetch('/api/data');
performance.mark('end-fetch');
performance.measure('fetch-duration', 'start-fetch', 'end-fetch');

const measures = performance.getEntriesByType('measure');
console.log(measures);
```

## 快速参考

| API | 使用场景 | 浏览器支持 |
|-----|----------|----------------|
| Fetch | HTTP 请求 | 现代浏览器 |
| Web Workers | CPU 密集型任务 | 现代浏览器 |
| Service Workers | 离线、缓存 | 现代浏览器 |
| IndexedDB | 大容量客户端存储 | 现代浏览器 |
| IntersectionObserver | 懒加载、无限滚动 | 现代浏览器 |
| MutationObserver | DOM 变化检测 | 现代浏览器 |
| Notifications | 用户提醒 | 现代浏览器（需权限） |
| Canvas | 2D 图形 | 所有浏览器 |
| WebGL | 3D 图形 | 现代浏览器 |
