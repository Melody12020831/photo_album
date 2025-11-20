import TagManagerView from '../views/TagManagerView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/tags',
      name: 'tags',
      component: TagManagerView,
      meta: { requiresAuth: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/upload',
      name: 'upload',
      component: () => import('../views/PhotoUploadView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/photos',
      name: 'photos',
      component: () => import('../views/PhotoWallView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/photos-old',
      name: 'photos-old',
      component: () => import('../views/PhotoWallView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/recover',
      name: 'recover',
      component: () => import('../views/RecoverView.vue'),
    },
  ],
})

router.beforeEach((to, from, next) => {
  const loggedIn = sessionStorage.getItem('token')

  if (to.matched.some(record => record.meta.requiresAuth) && !loggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router