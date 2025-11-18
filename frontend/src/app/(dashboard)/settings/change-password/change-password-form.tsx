'use client'

import { useState, useEffect, useRef } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Save, Loader2, CheckCircle } from "lucide-react"
import { updatePasswordSchema, UpdatePasswordSchemaType } from "./schema"
import { updatePassword } from "@/services/authService"

export function ChangePasswordForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [message, setMessage] = useState("")
  const [isError, setIsError] = useState(false)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  // Clear timeout
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])

  const { register, handleSubmit, formState: { errors }, reset } = useForm<UpdatePasswordSchemaType>({
    resolver: zodResolver(updatePasswordSchema),
  })

  const onSubmit = async (data: UpdatePasswordSchemaType) => {
    setIsLoading(true)
    setSaveSuccess(false)
    setIsError(false)
    
    try {
      const res = await updatePassword(data)
      setMessage(res.data.message)
      setIsError(false)
      reset()
    } catch (error: any) {
      console.error("Error updating password:", error)
      setIsError(true)
      setMessage(error.response.data.detail)
    } finally {
      setIsLoading(false)
      setSaveSuccess(true)
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      timeoutRef.current = setTimeout(() => setSaveSuccess(false), 3000)

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
              <Label htmlFor="old_password" className="text-sm font-medium">
                Current Password
              </Label>
              <div className="relative group">
                <Input
                  id="old_password"
                  type="password"
                  placeholder="Enter your current password"
                  className="pl-3 h-11 transition-all focus:ring-2 focus:ring-primary/20"
                  {...register("old_password")}
                />
              </div>
              {errors.old_password && (
                <p className="text-sm text-destructive">{errors.old_password.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="new_password" className="text-sm font-medium">
                New Password
              </Label>
              <div className="relative group">
                <Input
                  id="new_password"
                  type="password"
                  placeholder="Enter your new password"
                  className="pl-3 h-11 transition-all focus:ring-2 focus:ring-primary/20"
                  {...register("new_password")}
                />
              </div>
              {errors.new_password && (
                <p className="text-sm text-destructive">{errors.new_password.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm_new_password" className="text-sm font-medium">
                Confirm New Password
              </Label>
              <div className="relative group">
                <Input
                  id="confirm_new_password"
                  type="password"
                  placeholder="Confirm your new password"
                  className="pl-3 h-11 transition-all focus:ring-2 focus:ring-primary/20"
                  {...register("confirm_new_password")}
                />
              </div>
              {errors.confirm_new_password && (
                <p className="text-sm text-destructive">{errors.confirm_new_password.message}</p>
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
                <p className={`text-sm animate-in fade-in-50 ${
                  isError ? 'text-destructive' : 'text-green-600 dark:text-green-500'
                }`}>
                  {message}
                </p>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}