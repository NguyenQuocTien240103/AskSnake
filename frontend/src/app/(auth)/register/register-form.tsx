'use client'

import Link from 'next/link'
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useState } from "react"
import { registerSchema, RegisterSchemaType } from "@/app/(auth)/register/schema"
import { register as registerUser } from "@/services/authService"
import { useRouter } from 'next/navigation';

interface RegisterFormProps extends React.ComponentProps<"div"> {
  onSuccess?: () => void
}

export function RegisterForm({ className, onSuccess, ...props }: RegisterFormProps) {
  const [error, setError] = useState("")
  const router = useRouter();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<RegisterSchemaType>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: "",
      password: "",
      confirm_password: "",
    },
  })

  const onSubmit = async (data: RegisterSchemaType) => {
    try {
      setError("")
      await registerUser(data)
      router.push("/login");

    } catch (error) {
      setError('Registration failed. User might already exist.')
      console.error("Error:",error);
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="border-gray-200 dark:border-gray-800 shadow-2xl backdrop-blur-sm bg-white/80 dark:bg-gray-950/80">
        <CardHeader className="space-y-1 pb-4">
          <CardTitle className="text-2xl font-bold text-center">Register</CardTitle>
          <CardDescription className="text-center">
            Create a new account to get started
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {error && (
              <div className="text-red-600 dark:text-red-400 text-sm bg-red-50 dark:bg-red-950/30 p-3 rounded-lg border border-red-200 dark:border-red-900 text-center animate-in fade-in slide-in-from-top-2 duration-300">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                className="h-11 bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-800 focus:border-gray-400 dark:focus:border-gray-600 transition-colors"
                {...register("email")}
              />
              {errors.email && (
                <p className="text-sm text-red-500 animate-in fade-in slide-in-from-top-1 duration-200">
                  {errors.email.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                className="h-11 bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-800 focus:border-gray-400 dark:focus:border-gray-600 transition-colors"
                {...register("password")}
              />
              {errors.password && (
                <p className="text-sm text-red-500 animate-in fade-in slide-in-from-top-1 duration-200">
                  {errors.password.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm_password" className="text-sm font-medium">Confirm Password</Label>
              <Input
                id="confirm_password"
                type="password"
                placeholder="Confirm your password"
                className="h-11 bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-800 focus:border-gray-400 dark:focus:border-gray-600 transition-colors"
                {...register("confirm_password")}
              />
              {errors.confirm_password && (
                <p className="text-sm text-red-500 animate-in fade-in slide-in-from-top-1 duration-200">
                  {errors.confirm_password.message}
                </p>
              )}
            </div>

            <Button 
              type="submit" 
              className="w-full h-11 bg-gradient-to-r from-gray-900 to-gray-700 hover:from-gray-800 hover:to-gray-600 dark:from-white dark:to-gray-200 dark:hover:from-gray-100 dark:hover:to-gray-300 dark:text-gray-900 font-medium shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Create Account
            </Button>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-gray-200 dark:border-gray-800" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white dark:bg-gray-950 px-2 text-gray-500 dark:text-gray-400">
                  Or
                </span>
              </div>
            </div>

            <div className="text-center text-sm">
              <span className="text-gray-600 dark:text-gray-400">Already have an account?</span>{" "}
              <Link 
                href="/login" 
                className="font-medium text-gray-900 dark:text-white hover:underline underline-offset-4 transition-colors"
              >
                Login
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}