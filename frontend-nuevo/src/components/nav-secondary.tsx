"use client"

import * as React from "react"
import { useNavigate } from "react-router-dom"
import { type Icon } from "@tabler/icons-react"
import { Badge } from "@/components/ui/badge"

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

export function NavSecondary({
  items,
  unreadCount = 0,
  ...props
}: {
  items: {
    title: string
    url: string
    icon: Icon
  }[]
  unreadCount?: number
} & React.ComponentPropsWithoutRef<typeof SidebarGroup>) {
  const navigate = useNavigate()

  return (
    <SidebarGroup {...props}>
      <SidebarGroupContent>
        <SidebarMenu>
          {items.map((item) => {
            const isNotifications = item.title === "Notificaciones"
            return (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton onClick={() => navigate(item.url)} className="flex items-center gap-2">
                  <item.icon />
                  <span className="flex items-center gap-1">
                    {item.title}
                    {isNotifications && unreadCount > 0 && (
                      <Badge variant="destructive" className="text-[10px] leading-none h-4 min-w-4 px-1">
                        {unreadCount}
                      </Badge>
                    )}
                  </span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            )
          })}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  )
}
