'use client'

import Link from "next/link";
import { PanelsTopLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ChatPublicLayout({children}:{children: React.ReactNode}) {
    return (
        <div className="flex flex-col min-h-screen">
            <header className="z-[50] sticky top-0 w-full bg-background/95 border-b backdrop-blur-sm dark:bg-black/[0.6] border-border/40 flex justify-center">
                <div className="container h-14 flex items-center">
                    <Link
                    href="/"    
                    className="flex justify-start items-center hover:opacity-85 transition-opacity duration-300"
                    >
                    <PanelsTopLeft className="w-6 h-6 mr-3" />
                    <span className="font-bold">shadcn/ui sidebar</span>
                    </Link>
                    <nav className="ml-auto flex items-center gap-2">
                    <Button variant="default" asChild>
                        <Link href="/login" >
                            Login
                        </Link>
                    </Button>
                    <Button
                        variant="default"
                        asChild
                        className="bg-white text-black hover:bg-gray-100 border border-gray-300 dark:bg-black dark:text-white dark:hover:bg-zinc-800"
                        >
                        <Link href="/register">Register</Link>
                    </Button>
                    </nav>
                </div>
            </header>

            {children}
            
            <footer className="py-6 md:py-0 border-t border-border/40">
                <div className="flex flex-col items-center justify-center gap-4 md:h-24 md:flex-row">
                    <p className="text-balance text-center text-sm leading-loose text-muted-foreground">
                        Built on top of{" "}
                        <Link
                        href="https://ui.shadcn.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium underline underline-offset-4"
                        >
                        shadcn/ui
                        </Link>
                        . The source code is available on{" "}
                        <Link
                        href="https://github.com/salimi-my/shadcn-ui-sidebar"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium underline underline-offset-4"
                        >
                        GitHub
                        </Link>
                        .
                    </p>
                </div>
            </footer>
        </div>
    )
}
