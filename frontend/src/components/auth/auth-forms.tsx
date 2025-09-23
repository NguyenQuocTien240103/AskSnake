'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/lib/stores/auth'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  username: z.string().min(3, 'Username must be at least 3 characters'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

type LoginForm = z.infer<typeof loginSchema>
type RegisterForm = z.infer<typeof registerSchema>

interface AuthFormsProps {
  onSuccess?: () => void
}

export function AuthForms({ onSuccess }: AuthFormsProps) {
  const [isLogin, setIsLogin] = useState(true)
  const [error, setError] = useState('')
  const { login, register: registerUser, isLoading } = useAuthStore()

  const loginForm = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  })

  const registerForm = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      username: '',
      password: '',
      confirmPassword: '',
    },
  })

  const onLoginSubmit = async (data: LoginForm) => {
    setError('')
    const success = await login(data.email, data.password)
    if (success) {
      onSuccess?.()
    } else {
      setError('Invalid email or password')
    }
  }

  const onRegisterSubmit = async (data: RegisterForm) => {
    setError('')
    const success = await registerUser(data.email, data.username, data.password)
    if (success) {
      setIsLogin(true)
      registerForm.reset()
      setError('')
      // Show success message or auto-login
    } else {
      setError('Registration failed. User might already exist.')
    }
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>{isLogin ? 'Login' : 'Register'}</CardTitle>
        <CardDescription>
          {isLogin
            ? 'Enter your credentials to access your chat history'
            : 'Create an account to save your conversations'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="text-red-500 text-sm text-center bg-red-50 p-2 rounded">
            {error}
          </div>
        )}

        {isLogin ? (
          <form onSubmit={loginForm.handleSubmit(onLoginSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                {...loginForm.register('email')}
                disabled={isLoading}
              />
              {loginForm.formState.errors.email && (
                <p className="text-red-500 text-sm">{loginForm.formState.errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                {...loginForm.register('password')}
                disabled={isLoading}
              />
              {loginForm.formState.errors.password && (
                <p className="text-red-500 text-sm">{loginForm.formState.errors.password.message}</p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Logging in...' : 'Login'}
            </Button>
          </form>
        ) : (
          <form onSubmit={registerForm.handleSubmit(onRegisterSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="register-email">Email</Label>
              <Input
                id="register-email"
                type="email"
                {...registerForm.register('email')}
                disabled={isLoading}
              />
              {registerForm.formState.errors.email && (
                <p className="text-red-500 text-sm">{registerForm.formState.errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                {...registerForm.register('username')}
                disabled={isLoading}
              />
              {registerForm.formState.errors.username && (
                <p className="text-red-500 text-sm">{registerForm.formState.errors.username.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="register-password">Password</Label>
              <Input
                id="register-password"
                type="password"
                {...registerForm.register('password')}
                disabled={isLoading}
              />
              {registerForm.formState.errors.password && (
                <p className="text-red-500 text-sm">{registerForm.formState.errors.password.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-password">Confirm Password</Label>
              <Input
                id="confirm-password"
                type="password"
                {...registerForm.register('confirmPassword')}
                disabled={isLoading}
              />
              {registerForm.formState.errors.confirmPassword && (
                <p className="text-red-500 text-sm">{registerForm.formState.errors.confirmPassword.message}</p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Creating account...' : 'Register'}
            </Button>
          </form>
        )}

        <div className="text-center">
          <Button
            variant="link"
            onClick={() => {
              setIsLogin(!isLogin)
              setError('')
              loginForm.reset()
              registerForm.reset()
            }}
            disabled={isLoading}
          >
            {isLogin
              ? "Don't have an account? Register"
              : 'Already have an account? Login'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}