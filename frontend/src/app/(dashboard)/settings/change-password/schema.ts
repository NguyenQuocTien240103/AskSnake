import * as z from 'zod'

export const updatePasswordSchema = z
.object({
  old_password: z.string().min(6, "Password must be at least 6 characters"),
  new_password: z.string().min(6, "Password must be at least 6 characters"),
  confirm_new_password: z.string()
})
.refine((data) => data.new_password === data.confirm_new_password, {
  message: "Passwords don't match",
  path: ["confirm_new_password"],
});

export type UpdatePasswordSchemaType = z.infer<typeof updatePasswordSchema>
