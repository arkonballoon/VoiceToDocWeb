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

    <div class="main-container">
      <router-view></router-view>
    </div>
  </div>
</template>

<style>
:root {
  --primary-color: #FFB800;
  --secondary-color: #003366;
  --text-color: #2c3e50;
  --background-gradient: linear-gradient(135deg, #001428 0%, #004080 100%);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #f5f6fa;
}

.header {
  background: var(--background-gradient);
  padding: 1rem;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.nav-links {
  display: flex;
  gap: 2rem;
  justify-content: center;
}

.nav-links a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-links a.active,
.nav-links a:hover {
  background: rgba(255, 255, 255, 0.1);
}

.main-container {
  margin-top: 64px; /* Höhe der Header-Bar */
  padding: 2rem;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}
</style>
