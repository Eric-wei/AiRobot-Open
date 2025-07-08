<script>
/**
 * @Author: zhujinlong
 * @Date:   2025-04-17 19:51:55
 * @Last Modified by:   zhujinlong
 * @Last Modified time: 2025-04-23 16:10:20 // Update time if needed
 */
</script><template>
  <div class="chat-container">
    <ImagePreview 
      :show="showImagePreview" 
      :image-src="previewImageSrc" 
      @close="closeImagePreview"
    />
    <!-- 添加 CameraCapture 组件 -->
    <CameraCapture
      :show="showCameraCapture"
      @close="closeCameraCapture"
      @image-captured="handleImageCaptured"
    />
    <div class="header">
      <div class="agent-id">ID: {{ agentId }}</div>
      <button class="exit-button" @click="exitChat">退出</button>
    </div>
    
    <div style="width: 1px; height: 1px; overflow: hidden;">
      <div id="herevideo"></div>
      <div id="therevideo"></div>
    </div>

    <div class="messages-container" ref="messagesContainer">
      <div v-for="(message, index) in messages" :key="index" 
           :class="['message', message.role]">
        <div class="message-content">
          <div class="markdown-content" v-html="renderMarkdown(message.content)" @click="handleImageClick"></div>
        </div>
      </div>
    </div>
    
    <div class="input-container">
      <textarea
        v-model="userInput"
        @keydown.enter.prevent="sendMessage"
        placeholder="输入消息..."
        rows="3"
      ></textarea>
      <div class="button-group">
        <img 
          :src="isMuted ? '/icons/mic-off.svg' : '/icons/mic-on.svg'" 
          class="mic-icon" 
          @click="toggleMute"
        >
        <button @click="sendMessage" :disabled="!userInput.trim()">发送</button>
        <button class="file-upload-button" @click="triggerFileInput">选择图片</button>
        <!-- 添加拍照按钮 -->
        <button class="camera-button" @click="openCameraCapture">拍照</button>
        <span v-if="selectedFile" class="selected-file-name">{{ selectedFile.name }}</span>
      </div>
    </div>
    
    <div class="file-upload-container">
      <input 
        type="file" 
        id="fileInput" 
        ref="fileInput" 
        @change="handleFileChange" 
        class="file-input"
        accept="image/*"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useToast } from "vue-toastification"; 
import { marked } from 'marked'
import katex from 'katex'
import hljs from 'highlight.js'
import 'katex/dist/katex.min.css'
import 'highlight.js/styles/github.css'
import BaiduRtcAgentClient from '../services/BaiduRtcAgent'
import ImagePreview from './ImagePreview.vue'
// 导入 CameraCapture 组件
import CameraCapture from './CameraCapture.vue'
const toast = useToast(); 
const props = defineProps({
  appId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['exit-chat'])

const messages = ref([])
const userInput = ref('')
const messagesContainer = ref(null)
const agentId = ref('')
const isMuted = ref(false)
const showFileUpload = ref(true)
const selectedFile = ref(null)
const fileInput = ref(null)
const showImagePreview = ref(false)
const previewImageSrc = ref('')
const showCameraCapture = ref(false)
// 新增 ref 来记录打开摄像头前的麦克风状态
const wasMutedBeforeCamera = ref(false)

var ia_message_last = ''


// 创建BRTC Agent实例
const agent = new BaiduRtcAgentClient()

// 配置marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true
})

// 渲染Markdown
const renderMarkdown = (content) => {
  // 处理LaTeX公式
  content = content.replace(/\$\$(.*?)\$\$/g, (_, formula) => {
    try {
      return katex.renderToString(formula, { displayMode: true })
    } catch (e) {
      return formula
    }
  })
  content = content.replace(/\$(.*?)\$/g, (_, formula) => {
    try {
      return katex.renderToString(formula, { displayMode: false })
    } catch (e) {
      return formula
    }
  })
  content = content.replace(/\\\((.*?)\\\)/g, (_, formula) => {
    try {
      return katex.renderToString(formula, { displayMode: false })
    } catch (e) {
      return formula
    }
  })
  
  content = content.replace(/\\\[\n(.*?)\n\\\]/gs, (_, formula) => {
    try {
      return katex.renderToString(formula, { displayMode: false })
    } catch (e) {
      return formula
    }
  })
  
  content = content.replace(/\\\[(.*?)\\\]/gs, (_, formula) => {
    try {
      return katex.renderToString(formula, { displayMode: false })
    } catch (e) {
      return formula
    }
  })
  
  return marked(content)
}

// 格式化消息
const formatMessage = (msg) => {
  if (msg && (msg.startsWith('[Q]:') || msg.startsWith('[A]:'))) {
    var q = "assistant"
    if(msg.startsWith('[Q]:')){
      q = 'user'
    }
    msg = msg.substring(4);
    console.log(msg)
    msg = msg.replaceAll('\n', '<br>');
    return {
      role: q,
      content: msg
    };
  }

  return null

  

 
}

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim()) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userInput.value
  })

  // 发送消息到Agent
  agent.sendMessageToUser(userInput.value)

  // 清空输入框
  userInput.value = ''

  // 滚动到底部
  scrollToBottom()
}

// 发送中断信号
const sendBreak = () => {
  agent.sendMessageToUser('[B]')
}

// 切换麦克风状态 (保持不变)
const toggleMute = () => {
  isMuted.value = !isMuted.value
  if (isMuted.value) {
    window.BRTC_MuteMicphone(true)
  } else {
    window.BRTC_MuteMicphone(false)
  }
}

// 处理文件选择
const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    toast.warning('请选择图片文件')
    return
  }
  
  selectedFile.value = file
  sendFile(file)
}

// 发送文件 (保持不变, CameraCapture 会调用这个)
const sendFile = (file) => {
  if (!file || file.size === 0) return

  const chunkSize = 16384
  const fileReader = new FileReader()
  let offset = 0

  fileReader.addEventListener('error', error => console.error('Error reading file:', error))
  fileReader.addEventListener('abort', event => console.log('File reading aborted:', event))
  fileReader.addEventListener('load', e => {
    let hdr = ''
    if (offset === 0) {
      hdr = '\x18[T]=binary;[N]=' + file.name + '\n'
    } else {
      hdr = '\x10'
    }

    const bin_hdr = new TextEncoder().encode(hdr)
    const sendbuf = new Uint8Array(bin_hdr.length + e.target.result.byteLength)
    sendbuf.set(bin_hdr)
    sendbuf.set(new Uint8Array(e.target.result), bin_hdr.length)
    window.BRTC_SendData(sendbuf)

    offset += e.target.result.byteLength
    if (offset < file.size) {
      readSlice()
    } else {
      window.BRTC_SendData('\x14')

      if (file.type.startsWith('image/')) {
        const randomId = '100' + Math.floor(Math.random() * 1000000).toString()
        messages.value.push({
          role: 'user',
          content: `<img style="max-width: 300px;" id="preview${randomId}"/>`,
          file: 'image'
        })
        nextTick(() => {
          const img = document.getElementById('preview' + randomId)
          if (img) {
            const imgreader = new FileReader()
            imgreader.onload = (e) => {
              img.src = e.target.result
              img.onload = () => {
                scrollToBottom()
              }
            }
            imgreader.readAsDataURL(file)
          }
          scrollToBottom()
        })
      }
    }
  })

  const readSlice = () => {
    const slice = file.slice(offset, offset + chunkSize)
    fileReader.readAsArrayBuffer(slice)
  }

  readSlice()

  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 新增：从 URL 发送图片文件
const sendImageFromUrl = async (imageUrl) => {
  if (!imageUrl) {
    toast.error('请输入有效的图片URL');
    return;
  }

  try {
    // 1. 下载图片数据
    const response = await fetch(imageUrl);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 2. 创建 Blob 对象
    const blob = await response.blob();

    // 检查是否是图片类型 (可选但推荐)
    if (!blob.type.startsWith('image/')) {
       console.log('Downloaded file is not an image:', blob.type);
       toast.error('链接指向的不是有效的图片文件');
       return;
    }

    // 3. 创建 File 对象
    // 从 URL 中提取文件名 (这是一个基础实现，可能需要根据实际 URL 格式调整)
    let filename = imageUrl.substring(imageUrl.lastIndexOf('/') + 1);
    // 尝试移除 URL 参数
    const queryIndex = filename.indexOf('?');
    if (queryIndex !== -1) {
      filename = filename.substring(0, queryIndex);
    }
    // 如果文件名无效，提供一个默认名
    if (!filename) {
        filename = 'downloaded_image';
    }
    // 确保有文件扩展名 (如果原始 URL 没有)
     if (!filename.includes('.') && blob.type.split('/')[1]) {
         filename += '.' + blob.type.split('/')[1];
     }


    const imageFile = new File([blob], filename, { type: blob.type });

    // 4. 调用现有的 sendFile 函数
    console.log(`Sending file from URL: ${filename}, Size: ${imageFile.size}, Type: ${imageFile.type}`);
    sendFile(imageFile);

  } catch (error) {
    console.log('Error fetching or processing image from URL:', error);
    toast.error(`无法从URL加载图片: ${error.message}`);
  }
};

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 退出聊天
const exitChat = () => {
  agent.Stop().then(() => {
    console.log('Agent stopped.')
    localStorage.setItem('agent_state', 'stopped')
    emit('exit-chat')
  })
}

// 启动Agent
const startAgent = () => {
  const cfg = {
    llm: '',
    llm_url: '',
    lang: '',
    tts: '',
    asr: '',
    tag: 'H5.SDK',
    tts_sayhi: '',
    role: '',
    location: '',
    llm_cfg: '',
    asr_url: '',
    tts_url: '',
    audiocodec: '',
    xiling_auth: '',
    xiling_bgimg: '',
    fid: '',
    llm_token: ''
  }
  
  agent.Start({
    apihost: 'https://ai.agent.kaywang.cn/api',
    debuglevel: false,
    cfg: cfg,
    appid: props.appId,
    displayname: 'web chat',
    remotevideoviewid: 'therevideo',
    localvideoviewid: 'herevideo',
    usingremotemediastate: true,
    remotemediastating: function (id, medium, on) {
      console.log('receiving media id:' + id + ' medium:' + medium + ' :' + on)
    },
    userevent_joinedroom: function (id, display, attribute) {
      console.log('userevent_joinedroom id: ' + id
        + ', display: ' + display + ', attribute:' + attribute)
      
      messages.value.push({
        role: 'system',
        content: display + " 来了!"
      })
      scrollToBottom()
    },
    userevent_leavingroom: function (id, display) {
      console.log('userevent_leavingroom id: ' + id + ', display: ' + display)
      messages.value.push({
        role: 'system',
        content: display + " 走了～"
      })
    },
    success: function () {
      agentId.value = agent.GetAgentID()
      localStorage.setItem('agent_id', agentId.value)
      localStorage.setItem('agent_state', 'playing')
    },
    error: function (error) {
      console.log('BRTC: ' + error)
    },
    onmessage: function (msg) {
      console.log('onmessage id: ' + msg.id + ' data: ' + msg.data)

      if (msg.data.startsWith('[E]')) {
        // Event messages
        return
      } else if (msg.data.startsWith('[F]')) {
        // Function Call
        return
      }

      var rawMsg = msg.data;
      var last_message = null
      if (messages.value.length){
        last_message = messages.value[messages.value.length - 1];
        if(last_message.file){
          last_message = null
        }
      }
      
      if (rawMsg.startsWith('[Q]:')) {
        if (rawMsg.includes('[M]:') || rawMsg.includes('[C]:')) {
          rawMsg = rawMsg.replaceAll('[M]:', '').replaceAll('[C]:', '')
          if (last_message && last_message.role == "user") {
            rawMsg = rawMsg.replaceAll('[Q]:', '')
            last_message.content = rawMsg;
            return;
          }
        }else{
          if (last_message && last_message.role == "user") {
            rawMsg = rawMsg.replaceAll('[Q]:', '')
            last_message.content = rawMsg;
            return;
          }
        }
      } else if (rawMsg.startsWith('[A]:')) {
        if (rawMsg.includes('[M]:') || rawMsg.includes('[C]:')) {
          rawMsg = rawMsg.replaceAll('[M]:', '').replaceAll('[C]:', '')
          if (last_message && last_message.role == "assistant") {
            rawMsg = rawMsg.replaceAll('[A]:', '')
            ia_message_last = ia_message_last + rawMsg
            last_message.content = ia_message_last;
            return;
          }else{
            ia_message_last = rawMsg.replaceAll('[A]:', '')
          }
        }else{
          if (last_message && last_message.role == "assistant") {
            rawMsg = rawMsg.replaceAll('[A]:', '')
            last_message.content = rawMsg;
            ia_message_last = ''
            return;
          }
        } 
      }
      const formattedMsg = formatMessage(rawMsg)
      if(formattedMsg){
        messages.value.push(formattedMsg)      
        scrollToBottom()
      }
      
    }
  })
}


// 打开拍照界面
const openCameraCapture = () => {
  // 记录当前麦克风状态
  wasMutedBeforeCamera.value = isMuted.value;
  // 如果当前未静音，则强制静音
  if (!isMuted.value) {
    console.log('Muting microphone for camera capture.');
    window.BRTC_MuteMicphone(true);
    // 注意：这里不直接修改 isMuted.value，因为它反映的是用户手动设置的状态
  }
  showCameraCapture.value = true;
}

// 关闭拍照界面
const closeCameraCapture = () => {
  showCameraCapture.value = false;
  // 如果打开摄像头前麦克风是开启的，则恢复开启状态
  if (!wasMutedBeforeCamera.value) {
    console.log('Unmuting microphone after closing camera.');
    window.BRTC_MuteMicphone(false);
    // 同样，不直接修改 isMuted.value
  }
  // 可选：重置记录的状态
  // wasMutedBeforeCamera.value = false;
}

// 处理拍照组件捕获到的图片 (保持不变，因为它调用了 closeCameraCapture)
const handleImageCaptured = (imageFile) => {
  if (imageFile) {
    console.log('Received captured image in ChatInterface:', imageFile);
    sendFile(imageFile); // 使用现有的 sendFile 方法发送图片
  }
  closeCameraCapture(); // 关闭拍照界面 (会自动处理麦克风状态)
}


// 在 script setup 部分添加 triggerFileInput 方法
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleImageClick = (event) => {
  if (event.target.tagName === 'IMG') {
    previewImageSrc.value = event.target.src
    showImagePreview.value = true
  }
}

const closeImagePreview = () => {
  showImagePreview.value = false
  previewImageSrc.value = ''
}

onMounted(() => {
  // 确保音频初始化
  const initAudio = async () => {
    try {
      // 请求麦克风权限
      await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('Microphone permission granted');
      
      // 启动 agent
      startAgent();
    } catch (error) {
      console.log('Error initializing audio:', error);
      toast.error('未检查到语音设备')
    }
  };

  initAudio();
  scrollToBottom();
})

// 在组件卸载前停止 agent
onBeforeUnmount(() => {
  if (agent) {
    agent.Stop();
  }
})
</script>

<style>
@import '../styles/chat-interface.css';
/* 可以为拍照按钮添加一些样式 */
.camera-button {
  /* 样式与 file-upload-button 类似或自定义 */
  margin-left: 5px; /* 调整间距 */
}
</style>