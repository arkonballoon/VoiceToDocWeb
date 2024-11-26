<template>
  <div id="app">
    <header class="header">
      <nav class="nav">
        <div class="nav-links">
          <router-link to="/" :class="{ active: $route.path === '/' }">Transkription</router-link>
          <router-link to="/templates" :class="{ active: $route.path === '/templates' }">Templates</router-link>
        </div>
      </nav>
    </header>

    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
:root {
  --primary-color: #FFB800;
  --secondary-color: #003366;
  --text-color: #2c3e50;
  --background-gradient: linear-gradient(135deg, #001428 0%, #004080 100%);
}
</style>
