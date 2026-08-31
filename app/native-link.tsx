import type { AnchorHTMLAttributes, ReactNode } from "react";

type NativeLinkProps = AnchorHTMLAttributes<HTMLAnchorElement> & {
  href: string;
  children: ReactNode;
};

export default function NativeLink({ href, children, ...props }: NativeLinkProps) {
  return <a href={href} data-native-navigation="true" {...props}>{children}</a>;
}
