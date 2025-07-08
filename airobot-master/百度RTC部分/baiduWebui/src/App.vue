<script>
/**
 * @Author: zhujinlong
 * @Date:   2025-04-17 19:51:39
 * @Last Modified by:   zhujinlong
 * @Last Modified time: 2025-04-21 17:18:31
 */
</script><template>
  <div class="app-container">
    <RoomEntry v-if="!isChatStarted" @start-chat="startChat" />
    <ChatInterface v-else :appId="appId" @exit-chat="exitChat" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import RoomEntry from './components/RoomEntry.vue'
import ChatInterface from './components/ChatInterface.vue'

const isChatStarted = ref(false)
const appId = ref('')

// 开始聊天
const startChat = (id) => {
  appId.value = id
  isChatStarted.value = true
}

// 退出聊天
const exitChat = () => {
  isChatStarted.value = false
}
</script>

<style>
.app-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}
</style> 