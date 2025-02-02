"use client"

import { useState, useEffect, useRef } from "react"
import Head from "next/head"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import {
  ChevronDown,
  Globe,
  LayoutDashboard,
  MapPin,
  Menu,
  Phone,
  Settings,
  Store,
  MessageSquare,
} from "lucide-react"
import { Sidebar, SidebarContent, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"

// Import React Leaflet components
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet"

// Dummy store data
const stores = [
  {
    id: 1,
    name: "Green Grocer Market",
    address: "123 Food St, City",
    phone: "(555) 123-4567",
    status: "Active",
    donations: 75,
    requests: 3,
    // Example coordinates (New York)
    lat: 40.7128,
    lng: -74.006,
  },
  {
    id: 2,
    name: "Fresh Foods Co",
    address: "456 Market Ave, Town",
    phone: "(555) 234-5678",
    status: "Active",
    donations: 45,
    requests: 2,
    lat: 40.7138,
    lng: -74.005,
  },
  {
    id: 3,
    name: "Local Harvest",
    address: "789 Farm Rd, Village",
    phone: "(555) 345-6789",
    status: "Inactive",
    donations: 0,
    requests: 0,
    lat: 40.7148,
    lng: -74.004,
  },
]

// Dummy transcript messages
const transcriptMessages = [
  { role: "system", content: "Welcome to FoodConnect AI Assistant. How can I help you today?" },
  { role: "user", content: "Hi, I'd like to donate some food." },
  {
    role: "system",
    content: "That's great! We appreciate your generosity. Can you tell me what kind of food you'd like to donate?",
  },
  { role: "user", content: "I have some canned goods and fresh vegetables." },
  {
    role: "system",
    content:
      "Excellent! Both canned goods and fresh vegetables are always in high demand. Are these items still within their expiration dates?",
  },
]

export default function Page() {
  const [selectedStore, setSelectedStore] = useState(stores[0])
  const [transcript, setTranscript] = useState(transcriptMessages)
  const transcriptRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const interval = setInterval(() => {
      setTranscript((prev) => [
        ...prev,
        {
          role: Math.random() > 0.5 ? "user" : "system",
          content: `New message at ${new Date().toLocaleTimeString()}`,
        },
      ])
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight
    }
  }, [transcript])

  // Define map center based on the selected store's coordinates
  const mapCenter = [selectedStore.lat, selectedStore.lng] as [number, number]

  return (
    <SidebarProvider defaultOpen={false}>
      <Head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css"
          integrity="sha256-sA+4/7P+YkF1rN65g2X4F5x3S1tLFuM8Xz8aB1x0A+M="
          crossOrigin=""
        />
      </Head>
      <div className="flex h-screen overflow-hidden bg-[#F2F8F8]">
        {/* Sidebar */}
        <Sidebar collapsible="icon" className="bg-[#133223] text-white">
          <SidebarContent>
            <div className="flex h-16 items-center justify-between border-b border-[#55743B]/20 px-4">
              <div className="flex items-center gap-2">
                <Store className="h-6 w-6 text-[#32C58E]" />
                <span className="font-bold">FoodConnect</span>
              </div>
              <SidebarTrigger>
                <Menu className="h-6 w-6 text-[#F2F8F8]" />
              </SidebarTrigger>
            </div>
            <nav className="space-y-1 p-2">
              {[
                { name: "Dashboard", icon: LayoutDashboard },
                { name: "Locations", icon: MapPin },
                { name: "Analytics", icon: Globe },
                { name: "Settings", icon: Settings },
              ].map((item) => (
                <Button
                  key={item.name}
                  variant="ghost"
                  className="w-full justify-start gap-2 text-[#F2F8F8] hover:bg-white/10"
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Button>
              ))}
            </nav>
          </SidebarContent>
        </Sidebar>

        {/* Main Content */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Header */}
          <header className="flex h-16 items-center justify-between border-b border-[#55743B]/10 bg-white px-6">
            <h1 className="text-xl font-semibold text-[#133223]">Store Locations</h1>
            <div className="flex items-center gap-4">
              <Button variant="outline" className="gap-2">
                <Globe className="h-4 w-4" />
                All Regions
                <ChevronDown className="h-4 w-4" />
              </Button>
              <Button variant="outline" className="gap-2">
                <Settings className="h-4 w-4" />
                Filters
              </Button>
            </div>
          </header>

          {/* Map and Content */}
          <div className="flex flex-1 overflow-hidden">
            {/* Map Area using React Leaflet */}
            <div className="flex-1 relative">
              <MapContainer center={mapCenter} zoom={13} style={{ height: "100%", width: "100%" }}>
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                />
                <Marker position={mapCenter}>
                  <Popup>{selectedStore.name}</Popup>
                </Marker>
              </MapContainer>
            </div>

            {/* Right Sidebar */}
            <div className="w-96 flex flex-col border-l border-[#55743B]/10 bg-white">
              {/* Store Information */}
              <ScrollArea className="flex-1">
                <div className="p-4">
                  <h2 className="mb-4 text-lg font-semibold text-[#133223]">Store Information</h2>
                  <div className="space-y-4">
                    {stores.map((store) => (
                      <Card
                        key={store.id}
                        className={`cursor-pointer p-4 transition-all hover:shadow-md ${
                          selectedStore.id === store.id ? "ring-2 ring-[#32C58E]" : ""
                        }`}
                        onClick={() => setSelectedStore(store)}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-medium text-[#133223]">{store.name}</h3>
                            <div className="mt-1 text-sm text-[#55743B]">
                              <div className="flex items-center gap-1">
                                <MapPin className="h-4 w-4" /> {store.address}
                              </div>
                              <div className="flex items-center gap-1">
                                <Phone className="h-4 w-4" /> {store.phone}
                              </div>
                            </div>
                          </div>
                          <Badge
                            variant={store.status === "Active" ? "default" : "secondary"}
                            className={store.status === "Active" ? "bg-[#32C58E]" : "bg-[#55743B]"}
                          >
                            {store.status}
                          </Badge>
                        </div>
                        {store.status === "Active" && (
                          <div className="mt-3 grid grid-cols-2 gap-2 border-t border-[#55743B]/10 pt-3 text-sm">
                            <div>
                              <div className="text-[#55743B]">Donations</div>
                              <div className="font-medium text-[#133223]">{store.donations}kg</div>
                            </div>
                            <div>
                              <div className="text-[#55743B]">Requests</div>
                              <div className="font-medium text-[#133223]">{store.requests}</div>
                            </div>
                          </div>
                        )}
                      </Card>
                    ))}
                  </div>
                </div>
              </ScrollArea>

              {/* Live Transcript */}
              <div className="h-1/3 border-t border-[#55743B]/10">
                <div className="flex items-center justify-between bg-[#133223] px-4 py-2 text-white">
                  <h3 className="font-semibold">Live Transcript</h3>
                  <MessageSquare className="h-5 w-5" />
                </div>
                <ScrollArea className="h-[calc(100%-40px)]" ref={transcriptRef}>
                  <div className="p-4 space-y-2">
                    {transcript.map((message, index) => (
                      <div
                        key={index}
                        className={`p-2 rounded-lg ${
                          message.role === "user" ? "bg-[#32C58E]/10 ml-8" : "bg-[#55743B]/10 mr-8"
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SidebarProvider>
  )
}
