"use client"
import React, { useEffect, useState } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ContentLayout } from "@/components/dashboard/content-layout"
import { getUserCurrent } from '@/services/userService'
import { Skeleton } from "@/components/ui/skeleton"
import { useAuthStore } from "@/stores/use-auth"
import { useRouter, useParams } from 'next/navigation'
import { getAllHistoryPredict } from "@/services/historyPredict"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Image from "next/image"

interface PredictData {
  _id: string
  confident: string
  label: string
  file_name: string
  timestamp: string
}

const SpeciesDetailPage = () => {
  const router = useRouter()
  const params = useParams()
  const label = decodeURIComponent(params.label as string)
  console.log("Label from params:", label)
  const [page, setPage] = useState(1)
  const [images, setImages] = useState<PredictData[]>([])
  const { setLogin, setLogout } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const limit = 5
  
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await getUserCurrent()
        setLogin(res.data)
        setLoading(false)
      } catch (error: any) {
        console.error(error)
        
        if (error.response?.status === 401) {
          setLogout()
          router.push("/login")
          return
        }
      } 
    }
    fetchUser()
  }, [])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getAllHistoryPredict()
        console.log("Full data:", res.data)
        
        // Backend trả về: { status: "success", data: { items: [...], label_count: {...} } }
        const allItems = res.data.data.items || []
        // Lọc các ảnh theo label
        const filteredImages = allItems.filter((item: PredictData) => item.label === label)
        setImages(filteredImages)
      } catch (err) {
        console.error("Error fetching history predict:", err)
      }
    }
    fetchData()
  }, [label])

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('vi-VN')
  }

  // Pagination logic
  const total = images.length
  const totalPages = Math.ceil(total / limit)
  const startIndex = (page - 1) * limit
  const endIndex = startIndex + limit
  const currentPageData = images.slice(startIndex, endIndex)
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

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    )
  }

  return (
    <ContentLayout title={`Detail - ${label}`}>
      <div className="p-6">
        <div className="flex items-center gap-4 mb-4">
          <Button 
            onClick={() => router.back()} 
            variant="outline"
            size="sm"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">
            Detail: {label.replace(/_/g, ' ')}
          </h1>
        </div>

        <p className="text-gray-600 mb-4">Total images: {images.length}</p>

        <div className="[&_[data-slot=table-container]]:overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>No</TableHead>
                <TableHead>Image</TableHead>
                <TableHead>File Name</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead>Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {currentPageData.map((item, index) => (
                <TableRow key={item._id}>
                  <TableCell>{startIndex + index + 1}</TableCell>
                  <TableCell>
                    <div className="relative w-20 h-20">
                      <img
                        src={`http://localhost:8000/static/${item.file_name}`}
                      //   alt={item.label}
                      //   fill
                      //   className="object-cover rounded"
                      //   onError={(e) => {
                      //     // Fallback nếu ảnh không load được
                      //     (e.target as HTMLImageElement).src = '/placeholder.png'
                      //   }}
                      />
                    </div>
                  </TableCell>
                  <TableCell className="text-sm">{item.file_name}</TableCell>
                  <TableCell>{item.confident}</TableCell>
                  <TableCell className="text-sm">{formatTimestamp(item.timestamp)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {images.length === 0 && (
          <p className="text-center text-gray-500 mt-4">Không có ảnh nào cho loài này</p>
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

export default SpeciesDetailPage
