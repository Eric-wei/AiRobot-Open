<script>
/**
 * @Author: zhujinlong
 * @Date:   2025-04-22 11:04:39
 * @Last Modified by:   zhujinlong
 * @Last Modified time: 2025-04-22 11:08:03
 */
</script><template>
  <div v-if="show" class="image-preview-overlay" @click="close">
    <div class="image-preview-content">
      <img :src="imageSrc" class="preview-image" @click.stop>
      <button class="close-button" @click="close">×</button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  imageSrc: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}
</script>

<style scoped>
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.image-preview-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.preview-image {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
}

.close-button {
  position: absolute;
  top: -30px;
  right: -40px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: white;
  border: none;
  color: #333;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  min-width: 30px;
}

.close-button:hover {
  background-color: #f0f0f0;
}
</style> 