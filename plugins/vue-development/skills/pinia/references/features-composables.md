---
name: composables-in-stores
description: 在 Pinia store 中使用 Vue composables
---

# Store 中的 Composable

Pinia store 可以利用 Vue composables 来复用有状态逻辑。

## Option Store

在 `state` 属性内部调用 composable，但仅限返回可写 ref 的那些：

```ts
import { defineStore } from 'pinia'
import { useLocalStorage } from '@vueuse/core'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: useLocalStorage('pinia/auth/login', 'bob'),
  }),
})
```

**可用：** 返回 `ref()` 的 composable：
- `useLocalStorage`
- `useAsyncState`

**在 Option Store 中不可用：**
- 暴露函数的 composable
- 暴露只读数据的 composable

## Setup Store

更灵活 —— 几乎可以使用任何 composable：

```ts
import { defineStore } from 'pinia'
import { useMediaControls } from '@vueuse/core'
import { ref } from 'vue'

export const useVideoPlayer = defineStore('video', () => {
  const videoElement = ref<HTMLVideoElement>()
  const src = ref('/data/video.mp4')
  const { playing, volume, currentTime, togglePictureInPicture } =
    useMediaControls(videoElement, { src })

  function loadVideo(element: HTMLVideoElement, newSrc: string) {
    videoElement.value = element
    src.value = newSrc
  }

  return {
    src,
    playing,
    volume,
    currentTime,
    loadVideo,
    togglePictureInPicture,
  }
})
```

**注意：** 不要返回像 `videoElement` 这种不可序列化的 DOM ref —— 它们属于内部实现细节。

## SSR 注意事项

### Option Store 与 hydrate()

定义一个 `hydrate()` 函数处理客户端水合：

```ts
import { defineStore } from 'pinia'
import { useLocalStorage } from '@vueuse/core'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: useLocalStorage('pinia/auth/login', 'bob'),
  }),

  hydrate(state, initialState) {
    // 忽略服务端 state，从浏览器读取
    state.user = useLocalStorage('pinia/auth/login', 'bob')
  },
})
```

### Setup Store 与 skipHydrate()

标记不应从服务端水合的 state：

```ts
import { defineStore, skipHydrate } from 'pinia'
import { useEyeDropper, useLocalStorage } from '@vueuse/core'

export const useColorStore = defineStore('colors', () => {
  const { isSupported, open, sRGBHex } = useEyeDropper()
  const lastColor = useLocalStorage('lastColor', sRGBHex)

  return {
    // 跳过仅客户端 state 的水合
    lastColor: skipHydrate(lastColor),
    open,       // 函数 —— 无需水合
    isSupported, // 布尔值 —— 非响应式
  }
})
```

`skipHydrate()` 仅适用于 state 属性（ref），不适用于函数或非响应式值。

<!--
Source references:
- https://pinia.vuejs.org/cookbook/composables.html
-->
