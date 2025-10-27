'use client'

import * as z from "zod"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Save, Loader2, CheckCircle } from "lucide-react"

const passwordSchema = z.object({
  currentPassword: z.string().min(6, "Password must be at least 6 characters"),
  newPassword: z.string().min(6, "Password must be at least 6 characters"),
  confirmPassword: z.string()
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type PasswordFormValues = z.infer<typeof passwordSchema>

export function ChangePasswordForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<PasswordFormValues>({
    resolver: zodResolver(passwordSchema),
  })

  const onSubmit = async (data: PasswordFormValues) => {
    setIsLoading(true)
    setSaveSuccess(false)
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      console.log("Password data:", data)
      
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
      reset()
    } catch (error) {
      console.error("Error updating password:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl space-y-6">
      {/* Header Card */}
      <Card className="border-2 shadow-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">Change Password</CardTitle>
          <CardDescription>
            Update your password to keep your account secure
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Password Form */}
      <Card className="border-2 shadow-lg">
        <CardHeader>
          <CardTitle>Password Settings</CardTitle>
          <CardDescription>
            Enter your current password and choose a new one
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="currentPassword" className="text-sm font-medium">
                Current Password
              </Label>
              <div className="relative group">
                <Input
                  id="currentPassword"
                  type="password"
                  placeholder="Enter your current password"
                  className="pl-3 h-11 transition-all focus:ring-2 focus:ring-primary/20"
                  {...register("currentPassword")}
                />
              </div>
              {errors.currentPassword && (
                <p className="text-sm text-destructive">{errors.currentPassword.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="newPassword" className="text-sm font-medium">
                New Password
              </Label>
              <div className="relative group">
                <Input
                  id="newPassword"
                  type="password"
                  placeholder="Enter your new password"
                  className="pl-3 h-11 transition-all focus:ring-2 focus:ring-primary/20"
                  {...register("newPassword")}
                />
              </div>
              {errors.newPassword && (
                <p className="text-sm text-destructive">{errors.newPassword.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-sm font-medium">
                Confirm New Password
              </Label>
              <div className="relative group">
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Confirm your new password"
                  className="pl-3 h-11 transition-all focus:ring-2 focus:ring-primary/20"
                  {...register("confirmPassword")}
                />
              </div>
              {errors.confirmPassword && (
                <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
              )}
            </div>

            {/* Save Button */}
            <div className="flex items-center gap-3 pt-4">
              <Button
                type="submit"
                disabled={isLoading}
                className="min-w-[140px] h-11 font-medium group"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Updating...
                  </>
                ) : saveSuccess ? (
                  <>
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Updated!
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                    Update Password
                  </>
                )}
              </Button>
              
              {saveSuccess && (
                <p className="text-sm text-green-600 dark:text-green-500 animate-in fade-in-50">
                  Your password has been updated successfully!
                </p>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}