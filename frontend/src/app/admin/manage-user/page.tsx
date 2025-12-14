"use client"
import React, { useEffect, useState } from "react"
import { Table,TableBody,TableCell,TableHead,TableHeader,TableRow } from "@/components/ui/table"
import { ContentLayout } from "@/components/dashboard/content-layout"
import { getUsers } from "@/services/userService"
import { getUserCurrent } from '@/services/userService';
import { Skeleton } from "@/components/ui/skeleton";
import { useAuthStore } from "@/stores/use-auth";
import { useRouter } from 'next/navigation'


const ManageUserPage = () => {
  const router = useRouter();
  const [page, setPage] = useState(1)
  const [users, setUsers] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const limit = 10
  const {setLogin, setLogout} = useAuthStore();
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await getUserCurrent();
        setLogin(res.data)
        setLoading(false)
      } catch (error: any) {
        console.error(error);
        
        if(error.response?.status === 401){
          setLogout();
          router.push("/login")
          return;
        }

      } 
      // finally {
      //   setLoading(false)
      // }
    };
    fetchUser();
  }, []);


  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getUsers(page, limit)
        setUsers(res.data.data)
        setTotal(res.data.total)
      } catch (err) {
        console.error(err)
      }
    }
    fetchData()
  }, [page])

  const totalPages = Math.ceil(total / limit)

  // Pagination numbers
  const getPageNumbers = () => {
    const delta = 2
    const range: number[] = []
    const rangeWithDots: (number | string)[] = []
    let last: number | undefined

    for (let i = 1; i <= totalPages; i++) {
      if (
        i === 1 ||
        i === totalPages ||
        (i >= page - delta && i <= page + delta)
      ) {
        range.push(i)
      }
    }

    for (let i of range) {
      if (last !== undefined) {
        if (i - last === 2) {
          rangeWithDots.push(last + 1)
        } else if (i - last > 2) {
          rangeWithDots.push("...")
        }
      }
      rangeWithDots.push(i)
      last = i
    }

    return rangeWithDots
  }

  const startItem = (page - 1) * limit + 1
  const endItem = Math.min(page * limit, total)

  if(loading){
    return (
      <div className="space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-[400px] w-full" />
      </div>
    )
  }

  return (
    <ContentLayout title="Mange-User">
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Manage Users</h1>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>#</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user, index) => (
              <TableRow key={user._id}>
                <TableCell>{startItem + index}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.role}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {/* Pagination */}
        <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between border-t px-4 py-3">
          <p className="text-sm text-gray-700">
            Showing <span className="font-medium">{startItem}</span> to{" "}
            <span className="font-medium">{endItem}</span> of{" "}
            <span className="font-medium">{total}</span> results
          </p>

          <nav className="inline-flex -space-x-px rounded-md shadow-sm">
            <button
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              className="px-2 py-2 text-gray-400 hover:bg-gray-50"
            >
              ‹
            </button>

            {getPageNumbers().map((p, idx) =>
              p === "..." ? (
                <span
                  key={idx}
                  className="px-4 py-2 text-sm text-gray-500"
                >
                  ...
                </span>
              ) : (
                <button
                  key={idx}
                  onClick={() => setPage(p as number)}
                  className={`px-4 py-2 text-sm font-medium ${
                    p === page
                      ? "bg-indigo-600 text-white"
                      : "text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  {p}
                </button>
              )
            )}

            <button
              onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
              className="px-2 py-2 text-gray-400 hover:bg-gray-50"
            >
              ›
            </button>
          </nav>
        </div>
      </div>
    </ContentLayout>
  )
}

export default ManageUserPage
