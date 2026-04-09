import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo, UserRole } from '@/types/common'
import { mockLogin, roleMenus } from '@/mock/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('flood_token'))
  const user = ref<UserInfo | null>(
    localStorage.getItem('flood_user')
      ? JSON.parse(localStorage.getItem('flood_user')!)
      : null
  )

  const isAuthenticated = computed(() => !!token.value)
  const currentRole = computed<UserRole | null>(() => user.value?.role ?? null)
  const allowedMenus = computed(() =>
    currentRole.value ? roleMenus[currentRole.value] : []
  )

  function login(username: string, password: string): boolean {
    const result = mockLogin(username, password)
    if (result) {
      token.value = result.token
      user.value = result.user
      localStorage.setItem('flood_token', result.token)
      localStorage.setItem('flood_user', JSON.stringify(result.user))
      return true
    }
    return false
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('flood_token')
    localStorage.removeItem('flood_user')
  }

  function hasMenu(menuName: string): boolean {
    return allowedMenus.value.includes(menuName)
  }

  return {
    token,
    user,
    isAuthenticated,
    currentRole,
    allowedMenus,
    login,
    logout,
    hasMenu
  }
})
