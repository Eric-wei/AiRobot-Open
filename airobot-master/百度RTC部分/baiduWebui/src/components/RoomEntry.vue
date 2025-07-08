<script>
/**
 * @Author: zhujinlong
 * @Date:   2025-04-21 16:46:29
 * @Last Modified by:   zhujinlong
 * @Last Modified time: 2025-04-22 10:21:27
 */
</script><template>
  <div class="room-entry-container">
    <div class="room-entry-content">
      <div class="logo-container">
        <img src="https://brtc-sdk.cdn.bcebos.com/npm/baidurtc@1.0.1/demo/img/rtc_logo.png" class="logo-img">
        <div class="slogan">
          <div class="title-font-color">百度智能云RTC</div>
        </div>
      </div>
      
      <div class="agent-id" v-if="agentId">{{ agentId }}</div>
      
      
      
      <button 
        class="button big blue" 
        type="button" 
        @click="startChat" 
        :disabled="!appId.trim()"
      >
        开始通话
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const appId = ref('apprdep793ziq10')
const agentId = ref('')

// 从localStorage获取保存的appId
const savedAppId = localStorage.getItem('appid')
if (savedAppId) {
  appId.value = savedAppId
}

// 从localStorage获取保存的agentId
const savedAgentId = localStorage.getItem('agent_id')
if (savedAgentId) {
  agentId.value = 'id: ' + savedAgentId
}

// 开始聊天
const startChat = () => {
  if (!appId.value.trim()) return
  
  // 保存appId到localStorage
  localStorage.setItem('appid', appId.value)
  
  // 触发父组件的startChat事件
  emit('start-chat', appId.value)
}

// 定义emit
const emit = defineEmits(['start-chat'])
</script>

<style>
@import '../styles/room-entry.css';
</style> 