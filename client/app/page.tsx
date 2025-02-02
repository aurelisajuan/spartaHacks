"use client"

import { useState, useEffect, useRef, useMemo } from "react"
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
  Phone,
  Menu,
  Settings,
  Store,
  FileText
} from "lucide-react"
import { GoogleMapsEmbed } from '@next/third-parties/google'
import Image from 'next/image'

// Updated dummy store data with coordinates
const stores = [
  {
    id: 1,
    name: "Green Grocer Market",
    address: "123 Food St, City",
    phone: "(555) 123-4567",
    status: "Active",
    donations: 75,
    requests: 3,
    lat: 40.7128,
    lng: -74.0060,
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
    lng: -74.0070,
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
    lng: -74.0080,
  },
]

// Navigation items with icons
const navItems = [
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "Locations", icon: MapPin },
  { name: "Analytics", icon: Globe },
  { name: "Chats", icon: FileText },
  { name: "Settings", icon: Settings },
]

// Dummy transcript messages (initial)
const initialTranscript = [
  { role: "system", content: "Welcome to FoodConnect AI Assistant." },
  { role: "user", content: "Hi, I'd like to donate some food." },
]

export default function Page() {
  const [selectedStore, setSelectedStore] = useState(stores[0])
  const [sidebarExpanded, setSidebarExpanded] = useState(false)
  const [transcript, setTranscript] = useState(initialTranscript)
  const [apiKey, setApiKey] = useState<string | null>(null)
  const transcriptRef = useRef<HTMLDivElement>(null)

  // Load transcript messages periodically
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

  // Auto scroll to bottom when transcript updates
  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTo({
        top: transcriptRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [transcript]);  

  // Load Google Maps API key from env variable
  useEffect(() => {
    const key = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY as string
    setApiKey(key)
  }, [])

  // Memoize the GoogleMapsEmbed component to prevent reloading on transcript updates
  const GoogleMapsComponent = useMemo(() => {
    return apiKey ? (
      <GoogleMapsEmbed
        apiKey={apiKey}
        height={760}
        width="100%"
        mode="place"
        q={`${selectedStore.lat},${selectedStore.lng}`}
      />
    ) : null
  }, [apiKey, selectedStore])

  return (
    <>
      <Head>
        <title>FoodConnect - Store Locations</title>
      </Head>
      <div className="flex max-h-screen bg-[#F2F8F8] overflow-hidden">
        {/* Left Sidenav */}
        <aside
          className={`bg-[#133223] text-white transition-all duration-300 ${
            sidebarExpanded ? "w-64" : "w-16"
          }`}
        >
          <div className="flex h-16 items-center justify-between px-3 border-b border-[#55743B]/20">
            {sidebarExpanded && (
              <div className="flex items-center gap-2">
                {/* <Store className="h-6 w-6 text-[#32C58E]" /> */}
                <Image src="/logo.png" width={50} height={50} alt="logo" />
                <span className="font-bold">TFT</span>
              </div>
            )}
            <Button
              variant="ghost"
              onClick={() => setSidebarExpanded((prev) => !prev)}
              className="p-2"
            >
              <Menu className="h-6 w-6 rounded-xl hover:bg-[#32C58E] hover:rounded-xl" />
            </Button>
          </div>
          <nav className="p-2 space-y-1">
            {navItems.map((item) => (
                <Button
                key={item.name}
                variant="ghost"
                className={`w-full justify-center sm:justify-start gap-2 rounded-md hover:bg-[#32C58E] hover:rounded-md ${sidebarExpanded ? "p-2" : ""}`}
                >
                <item.icon className="h-5 w-5" />
                {sidebarExpanded && <span>{item.name}</span>}
                </Button>
            ))}
          </nav>
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="flex h-16 items-center justify-between border-b border-[#55743B]/10 bg-white p-6">
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

          {/* Main content below header: Map and Store Information */}
          <div className="flex flex-1">
            {/* Map Area */}
            <div className="flex-1">
              {GoogleMapsComponent}
            </div>

            {/* Right Store Information Panel */}
            <div className="w-96 flex flex-col bg-white border-l border-[#55743B]/10" style={{ height: "calc(100vh - 4rem)" }}>
              <div className="flex-1 p-4 border-b border-[#55743B]/10 overflow-auto">
                <h2 className="mb-4 text-lg font-semibold text-[#133223]">Store Information</h2>
                <div className="space-y-4">
                  {stores.map((store) => (
                    <Card
                      key={store.id}
                      onClick={() => setSelectedStore(store)}
                      className={`cursor-pointer p-4 transition-all hover:shadow-md bg-white ${
                        selectedStore.id === store.id ? "ring-2 ring-[#32C58E]" : ""
                      }`}
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
                          className={store.status === "Active" ? "bg-[#32C58E] text-white" : "bg-[#55743B] text-white"}
                        >
                          {store.status}
                        </Badge>
                      </div>
                      {/* {store.status === "Active" && (
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
                      )} */}
                    </Card>
                  ))}
                </div>
              </div>

              {/* Live Transcript */}
              <div className="flex-1 border-t border-[#55743B]/10 h-1/2">
                <div className="px-4 py-2 border-b border-[#55743B]/10">
                  <h2 className="text-lg font-semibold text-[#133223]">Live Transcript</h2>
                </div>
                <ScrollArea
                  className="h-[calc(100%-2.5rem)] overflow-y-auto"
                  ref={transcriptRef}
                >
                  <div className="space-y-2 p-2">
                    {transcript.map((msg, index) => (
                      <div
                        key={index}
                        className={`p-2 rounded-lg ${
                          msg.role === "user" ? "bg-[#32C58E]/10 ml-8" : "bg-[#55743B]/10 mr-8"
                        }`}
                      >
                        <p className="text-sm text-[#133223]">{msg.content}</p>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
