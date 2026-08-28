import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host") ?? "localhost:3000";
  const protocol = requestHeaders.get("x-forwarded-proto") ?? (host.startsWith("localhost") ? "http" : "https");
  const imageUrl = `${protocol}://${host}/og.png`;
  const title = "食用菌出海市场决策平台｜因恒科技";
  const description = "为菌企提供跨区域贸易、价格、渠道、物流与市场进入决策支持，重点深化老挝市场。";

  return {
    title,
    description,
    openGraph: { title, description, type: "website", locale: "zh_CN", images: [{ url: imageUrl, width: 1536, height: 1024, alt: "因恒科技食用菌出海数据与市场研究平台" }] },
    twitter: { card: "summary_large_image", title, description, images: [imageUrl] },
  };
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN"><body>{children}</body></html>;
}
