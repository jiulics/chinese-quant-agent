<template>
  <div class="view">
    <div class="page-head">
      <h1>Skill 中心</h1>
      <p>创建和管理自定义数据获取技能，扩展数据源与获取逻辑</p>
    </div>

    <el-empty v-if="!skills.length" description="暂无已注册技能" />
    <div v-else class="grid">
      <el-card v-for="s in skills" :key="s.name" class="skill-card" shadow="never">
        <template #header>
          <div class="skill-head">
            <span class="skill-name">{{ s.name }}</span>
            <el-tag size="small" :type="s.source === 'builtin' ? 'info' : 'success'">{{ s.source }}</el-tag>
          </div>
        </template>
        <p class="desc">{{ s.description }}</p>
        <div class="params" v-if="s.parameters?.properties">
          <div class="params-title">参数：</div>
          <el-tag v-for="(_, k) in s.parameters.properties" :key="k" size="small" class="param">{{ k }}</el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listSkills } from '@/api'

const skills = ref<any[]>([])

onMounted(async () => {
  skills.value = await listSkills()
})
</script>

<style scoped>
.view { max-width: 960px; margin: 0 auto; }
.page-head h1 { font-size: 24px; margin-bottom: 4px; }
.page-head p { color: var(--text-dim); font-size: 13px; margin-bottom: 20px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.skill-card { background: var(--card); border: 1px solid var(--border); }
.skill-head { display: flex; justify-content: space-between; align-items: center; }
.skill-name { font-weight: 600; }
.desc { color: var(--text-dim); font-size: 13px; line-height: 1.6; margin-bottom: 12px; }
.params-title { color: var(--text-dim); font-size: 12px; margin-bottom: 6px; }
.param { margin-right: 6px; }
</style>
