'use client'

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
import Link from 'next/link'

interface RegisterFormProps extends React.ComponentProps<"div"> {
  onSuccess?: () => void
}

export function RegisterForm({ className, onSuccess, ...props }: RegisterFormProps) {
  const [error, setError] = useState('')
  const router = useRouter();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<RegisterSchemaType>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      confirm_password: '',
    },
  })

  const onSubmit = async (data: RegisterSchemaType) => {
    try {
      setError('')
      await registerUser(data)
      router.push("/login");

    } catch (error) {
      setError('Registration failed. User might already exist.')
      console.error("Error:",error);
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle>Create your account</CardTitle>
          <CardDescription>
            Enter your email and password to register
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-6">
            {error && (
              <div className="text-red-500 text-sm bg-red-100 p-2 rounded text-center">
                {error}
              </div>
            )}

            <div className="grid gap-3">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                {...register("email")}
              />
              {errors.email && (
                <p className="text-sm text-red-500">{errors.email.message}</p>
              )}
            </div>

            <div className="grid gap-3">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                {...register("password")}
              />
              {errors.password && (
                <p className="text-sm text-red-500">{errors.password.message}</p>
              )}
            </div>

            <div className="grid gap-3">
              <Label htmlFor="confirm_password">Confirm Password</Label>
              <Input
                id="confirm_password"
                type="password"
                {...register("confirm_password")}
              />
              {errors.confirm_password && (
                <p className="text-sm text-red-500">
                  {errors.confirm_password.message}
                </p>
              )}
            </div>

            <div className="flex flex-col gap-3">
              <Button type="submit" className="w-full">
                Register
              </Button>
            </div>

            <div className="mt-4 text-center text-sm">
              Already have an account?{" "}
              < Link href="/login" className="underline underline-offset-4">
                Login
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
