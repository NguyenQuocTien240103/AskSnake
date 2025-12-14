import DashboardLayout from "@/components/dashboard/layout";
// import "@heroui/theme/dist/theme.css";

export default function MainLayout({ children }: { children: React.ReactNode}) {
    return <DashboardLayout>{children}</DashboardLayout>;
}
