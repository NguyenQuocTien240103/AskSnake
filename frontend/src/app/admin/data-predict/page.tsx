"use client"
import React, { useEffect, useState } from "react"
import { Table,TableBody,TableCell,TableHead,TableHeader,TableRow } from "@/components/ui/table"
import { ContentLayout } from "@/components/dashboard/content-layout"
import { getUserCurrent } from '@/services/userService';
import { Skeleton } from "@/components/ui/skeleton";
import { useAuthStore } from "@/stores/use-auth";
import { useRouter } from 'next/navigation'
import { getAllHistoryPredict } from "@/services/historyPredict"
import { Button } from "@/components/ui/button"

const DataPredictPage = () => {
  const router = useRouter();
  const [page, setPage] = useState(1)
  const [labelCount, setLabelCount] = useState<Record<string, number>>({})
  const {setLogin, setLogout} = useAuthStore();
  const [loading, setLoading] = useState(true);
  const limit = 5
  
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
    };
    fetchUser();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getAllHistoryPredict()
        console.log("History Predict Data:", res.data)
        // Backend trả về: { status: "success", data: { items: [...], label_count: {...} } }
        setLabelCount(res.data.data.label_count || {})
      } catch (err) {
        console.error("Error fetching history predict:", err)
      }
    }
    fetchData()
  }, [])

  const handleViewDetail = (label: string) => {
    router.push(`/admin/data-predict/${encodeURIComponent(label)}`)
  }

  // Pagination logic
  const labelEntries = Object.entries(labelCount)
  const total = labelEntries.length
  const totalPages = Math.ceil(total / limit)
  const startIndex = (page - 1) * limit
  const endIndex = startIndex + limit
  const currentPageData = labelEntries.slice(startIndex, endIndex)
  const startItem = startIndex + 1
  const endItem = Math.min(endIndex, total)

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

  if(loading){
    return (
      <div className="space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-[400px] w-full" />
      </div>
    )
  }

  return (
    <ContentLayout title="Data Predict">
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Data predicting snake species</h1>

        <div className="[&_[data-slot=table-container]]:overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>No</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Count</TableHead>
                <TableHead>Detail</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {currentPageData.map(([label, count], index) => (
                <TableRow key={label}>
                  <TableCell>{startIndex + index + 1}</TableCell>
                  <TableCell>{label.replace(/_/g, ' ')}</TableCell>
                  <TableCell>{count}</TableCell>
                  <TableCell>
                    <Button 
                      onClick={() => handleViewDetail(label)}
                      variant="outline"
                      size="sm"
                    >
                      Detail
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {Object.keys(labelCount).length === 0 && (
          <p className="text-center text-gray-500 mt-4">Chưa có dữ liệu dự đoán</p>
        )}

        {/* Pagination */}
        {total > 0 && (
          <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between border-t px-4 py-3">
            <p className="text-sm text-gray-700">
              Showing <span className="font-medium">{startItem}</span> to{" "}
              <span className="font-medium">{endItem}</span> of{" "}
              <span className="font-medium">{total}</span> results
            </p>

            <nav className="inline-flex -space-x-px rounded-md shadow-sm">
              <button
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                disabled={page === 1}
                className="px-2 py-2 text-gray-400 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
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
                disabled={page === totalPages}
                className="px-2 py-2 text-gray-400 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ›
              </button>
            </nav>
          </div>
        )}
      </div>
    </ContentLayout>
  )
}

export default DataPredictPage
