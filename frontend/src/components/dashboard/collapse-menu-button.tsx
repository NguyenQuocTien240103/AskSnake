"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ChevronDown, Dot, LucideIcon, MoreVertical, Trash2, Edit } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { DropdownMenuArrow } from "@radix-ui/react-dropdown-menu"; 
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"; 
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip"; 
import { DropdownMenu, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { usePathname } from "next/navigation";
import { deleteChat, renameChat } from "@/services/chatService"


type Submenu = {
  href: string;
  label: string;
  icon?: LucideIcon;
  active?: boolean;
};

interface CollapseMenuButtonProps {
  icon: LucideIcon;
  label: string;
  active: boolean;
  submenus: Submenu[];
  isOpen: boolean | undefined;
  isScrollDown?: boolean;
  // onRename?: (index: number, newLabel: string) => Promise<void>;
  // onDelete?: (index: number) => Promise<void>;
}

export function CollapseMenuButton({ 
  icon: Icon, 
  label, 
  active, 
  submenus, 
  isOpen, 
  isScrollDown,
  // onRename,
  // onDelete 
}: CollapseMenuButtonProps) {
  const pathname = usePathname();
  const isSubmenuActive = submenus.some((submenu) =>
    submenu.active === undefined ? submenu.href === pathname : submenu.active
  );
  const [isCollapsed, setIsCollapsed] = useState<boolean>(isSubmenuActive);
  const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [newName, setNewName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [openMenuIndex, setOpenMenuIndex] = useState<number | null>(null);
  const [localSubmenus, setLocalSubmenus] = useState<Submenu[]>(submenus);

  useEffect(() => {
    if(submenus.length !== localSubmenus.length){
      setLocalSubmenus(submenus);
    }
  }, [submenus]);
  // Mở dialog đổi tên
  const handleOpenRenameDialog = (index: number, currentLabel: string, href: string) => {
    setEditingIndex(index);
    setNewName(currentLabel);
    setIsRenameDialogOpen(true);
  };

  // Đóng dialog
  const handleCloseDialog = () => {
    setIsRenameDialogOpen(false);
    setEditingIndex(null);
    setNewName("");
  };


  const handleRename = async () => {
    if (editingIndex === null) return;

    const trimmedName = newName.trim();
    if (!trimmedName) {
      alert("Tên không được để trống!");
      return;
    }
    // console.log(localSubmenus[editingIndex])

    // Cập nhật giao diện ngay lập tức
    // setLocalSubmenus((prev) =>
    //   prev.map((item, i) =>
    //     i === editingIndex ? { ...item, label: trimmedName } : item
    //   )
    // );
    try {
      await renameChat(localSubmenus[editingIndex].href.split('/chats/').pop() || "",trimmedName);
      // Cập nhật giao diện ngay lập tức
      setLocalSubmenus((prev) =>
        prev.map((item, i) =>
          i === editingIndex ? { ...item, label: trimmedName } : item
      ));
    } catch (error) {
      console.error("Error deleting:", error);
      alert("Đổi tên thất bại!");
    }


  handleCloseDialog();
};


  // Xử lý xóa
  const handleDelete = async (index: number, label: string) => {
    if (confirm(`Bạn có chắc chắn muốn xóa "${label}"?`)) {
      try {
        await deleteChat(localSubmenus[index].href.split('/chats/').pop() || "");
        setLocalSubmenus(prev => prev.filter((_, i) => i !== index));
      } catch (error) {
        console.error("Error deleting:", error);
        alert("Xóa thất bại!");
      }
    }
  };

  // Xử lý Enter trong input
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleRename();
    }
  };

  return (
    <>
      {isOpen ? (
    <Collapsible
      open={isCollapsed}
      onOpenChange={setIsCollapsed}
      className="w-full"
    >
      <CollapsibleTrigger
        className="[&[data-state=open]>div>div>svg]:rotate-180 mb-1"
        asChild
      >
        <Button
          variant={isSubmenuActive ? "secondary" : "ghost"}
          className="w-full justify-start h-10"
        >
          <div className="w-full items-center flex justify-between">
            <div className="flex items-center">
              <span className="mr-4">
                <Icon size={18} />
              </span>
              <p
                className={cn(
                  "max-w-[150px] truncate",
                  isOpen
                    ? "translate-x-0 opacity-100"
                    : "-translate-x-96 opacity-0"
                )}
              >
                {label}
              </p>
            </div>
            <div
              className={cn(
                "whitespace-nowrap",
                isOpen
                  ? "translate-x-0 opacity-100"
                  : "-translate-x-96 opacity-0"
              )}
            >
              <ChevronDown
                size={18}
                className="transition-transform duration-200"
              />
            </div>
          </div>
        </Button>
      </CollapsibleTrigger>
      {
        isScrollDown ? (
          <CollapsibleContent className={cn(
                    "overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down",
                    localSubmenus.length > 3 && "max-h-40 overflow-y-auto"
                  )}>

                    {localSubmenus.map(({ href, icon: Icon, label, active }, index) => (
                        <div key={index} className="relative group">

                          {/* Nút submenu */}
                          <Button
                            variant={
                              (active === undefined && pathname === href) || active
                                ? "secondary"
                                : "ghost"
                            }
                            className="w-full justify-start h-10 mb-1"
                            asChild
                          >
                            <Link href={href}>
                              <span className="mr-4 ml-2">
                                {Icon ? <Icon size={18} /> : <Dot size={18} />}
                              </span>
                              <p
                                className={cn(
                                  "max-w-[140px] truncate",
                                  isOpen ? "translate-x-0 opacity-100" : "-translate-x-96 opacity-0"
                                )}
                                onClick={(e) => {
                                  if (pathname === href) {
                                    e.preventDefault();
                                    window.location.href = href;
                                  }
                                }}
                              >
                                {label}
                              </p>
                            </Link>
                          </Button>

                      {/* === DROPDOWN MENU MỚI === */}
                      <DropdownMenu
                        open={openMenuIndex === index}
                        onOpenChange={(isOpen) => setOpenMenuIndex(isOpen ? index : null)}
                      >
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="absolute right-1 top-1/2 -translate-y-1/2 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreVertical size={14} />
                          </Button>
                        </DropdownMenuTrigger>

                        <DropdownMenuContent align="end" side="right" sideOffset={5}>
                          {/* Đổi tên */}
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.preventDefault();
                              setOpenMenuIndex(null); // ⬅ Đóng menu ngay lập tức
                              handleOpenRenameDialog(index, label, href);
                            }}
                          >
                            <Edit size={14} className="mr-2" />
                            Đổi tên
                          </DropdownMenuItem>

                          {/* Xóa */}
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.preventDefault();
                              setOpenMenuIndex(null); // ⬅ Đóng menu
                              handleDelete(index, label);
                            }}
                            className="text-destructive focus:text-destructive"
                          >
                            <Trash2 size={14} className="mr-2" />
                            Xóa
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  ))}
          </CollapsibleContent>
        ) : (
          <CollapsibleContent className={cn(
            "overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down",
            submenus.length > 3 && "max-h-40 overflow-y-auto"
          )}>

            {submenus.map(({ href, icon: Icon, label, active }, index) => (
                <div key={index} className="relative group">

                  {/* Nút submenu */}
                  <Button
                    variant={
                      (active === undefined && pathname === href) || active
                        ? "secondary"
                        : "ghost"
                    }
                    className="w-full justify-start h-10 mb-1"
                    asChild
                  >
                    <Link href={href}>
                      <span className="mr-4 ml-2">
                        {Icon ? <Icon size={18} /> : <Dot size={18} />}
                      </span>
                      <p
                        className={cn(
                          "max-w-[140px] truncate",
                          isOpen ? "translate-x-0 opacity-100" : "-translate-x-96 opacity-0"
                        )}
                        onClick={(e) => {
                          if (pathname === href) {
                            e.preventDefault();
                            window.location.href = href;
                          }
                        }}
                      >
                        {label}
                      </p>
                    </Link>
                  </Button>
            </div>
          ))}

          </CollapsibleContent>
        )
      }
    </Collapsible>
  ) : (
    <DropdownMenu>
      <TooltipProvider disableHoverableContent>
        <Tooltip delayDuration={100}>
          <TooltipTrigger asChild>
            <DropdownMenuTrigger asChild>
              <Button
                variant={isSubmenuActive ? "secondary" : "ghost"}
                className="w-full justify-start h-10 mb-1"
              >
                <div className="w-full items-center flex justify-between">
                  <div className="flex items-center">
                    <span className={cn(isOpen === false ? "" : "mr-4")}>
                      <Icon size={18} />
                    </span>
                    <p
                      className={cn(
                        "max-w-[200px] truncate",
                        isOpen === false ? "opacity-0" : "opacity-100"
                      )}
                    >
                      {label}
                    </p>
                  </div>
                </div>
              </Button>
            </DropdownMenuTrigger>
          </TooltipTrigger>
          <TooltipContent side="right" align="start" alignOffset={2}>
            {label}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
      <DropdownMenuContent side="right" sideOffset={25} align="start">
        <DropdownMenuLabel className="max-w-[190px] truncate">
          {label}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {submenus.map(({ href, label, active }, index) => (
          <DropdownMenuItem key={index} asChild>
            <Link
              className={`cursor-pointer ${
                ((active === undefined && pathname === href) || active) &&
                "bg-secondary"
              }`}
              href={href}
            >
              <p className="max-w-[180px] truncate">{label}</p>
            </Link>
          </DropdownMenuItem>
        ))}
        <DropdownMenuArrow className="fill-border" />
      </DropdownMenuContent>
    </DropdownMenu>
      )}

      {/* Dialog đổi tên */}
      <Dialog open={isRenameDialogOpen} onOpenChange={setIsRenameDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Đổi tên</DialogTitle>
            <DialogDescription>
              Nhập tên mới cho mục này. Nhấn Enter hoặc click Lưu để xác nhận.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Tên mới</Label>
              <Input
                id="name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Nhập tên mới..."
                autoFocus
                disabled={isSubmitting}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleCloseDialog}
              disabled={isSubmitting}
            >
              Hủy
            </Button>
            <Button
              type="button"
              onClick={handleRename}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Đang lưu..." : "Lưu"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
