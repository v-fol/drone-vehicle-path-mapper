import React from "react";
import BaseMap from "@/components/BaseMap";
import FoundVehiclesList from "@/components/FoundVehiclesList";
import DroneFootageVideo from "@/components/DroneFootageVideo";
import PathJson from "@/pathGEO.json";

import { useAutoAnimate } from "@formkit/auto-animate/react";

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";

import { useAtom } from "jotai";
import {
  isAnimatingAtom,
  visibleDataAtom,
  currentIndexAtom,
  foundVehiclesImagesAtom,
  mapStyleAtom,
  selectedVehicleAtom,
} from "@/atoms";

const listOfthemes = [
  { name: "Dark", value: "mapbox://styles/mapbox/dark-v11" },
  { name: "Light", value: "mapbox://styles/mapbox/light-v11" },
  { name: "Satellite", value: "mapbox://styles/mapbox/satellite-v9" },
  {
    name: "Satellite Streets",
    value: "mapbox://styles/mapbox/satellite-streets-v12",
  },
  { name: "Streets", value: "mapbox://styles/mapbox/streets-v12" },
  { name: "Outdoors", value: "mapbox://styles/mapbox/outdoors-v12" },
  { name: "Navigation Day", value: "mapbox://styles/mapbox/navigation-day-v1" },
  {
    name: "Navigation Night",
    value: "mapbox://styles/mapbox/navigation-night-v1",
  },
];

export default function Home() {
  const [parent, enableAnimations] = useAutoAnimate(/* optional config */);

  const [isAnimating, setIsAnimating] = useAtom(isAnimatingAtom);
  const [visibleData, setVisibleData] = useAtom(visibleDataAtom);
  const [currentIndex, setCurrentIndex] = useAtom(currentIndexAtom);
  const [foundVehiclesImages, setFoundVehiclesImages] = useAtom(
    foundVehiclesImagesAtom
  );

  const [selectedVehicle, setSelectedVehicle] = useAtom(selectedVehicleAtom);

  const [mapStyle, setMapStyle] = useAtom(mapStyleAtom);

  const restartAnimation = () => {
    setVisibleData({ type: "FeatureCollection", features: [] });
    setCurrentIndex(0);
    setFoundVehiclesImages([]);
    setSelectedVehicle(null);

    // this is so that the video will restart
    setIsAnimating(false);
    setTimeout(() => {
      setIsAnimating(true);
    }, 100);
  };

  const forwardToEnd = () => {
    setVisibleData({
      type: "FeatureCollection",
      features: [...PathJson.features] as GeoJSON.Feature[],
    });

    const foundVehiclesImagesList = [];
    for (let i = 0; i < PathJson.features.length; i++) {
      if (foundVehiclesImagesList.length === 0) {
        foundVehiclesImagesList.push({
          vehicle_id: PathJson.features[i].properties.vehicle_id,
          confidence: 0.9,
          color: PathJson.features[i].properties.color,
        });
      }
      const found = foundVehiclesImagesList.find(
        (vehicle) =>
          vehicle.vehicle_id === PathJson.features[i].properties.vehicle_id
      );
      if (!found) {
        foundVehiclesImagesList.push({
          vehicle_id: PathJson.features[i].properties.vehicle_id,
          confidence: 0.9,
          color: PathJson.features[i].properties.color,
        });
      }
    }

    setFoundVehiclesImages(foundVehiclesImagesList);

    setCurrentIndex(PathJson.features.length);
    setIsAnimating(false);
  };

  return (
    <>
      <div className="h-[96vh]">
        <div className="px-8 flex justify-between mb-4 pt-8">
          <div className="flex gap-4">
            <button
              className="bg-zinc-5 rounded-lg px-4 text-zinc-300 text-xs sm:text-base hover:!bg-zinc-200 hover:text-zinc-800 border border-1 border-zinc-700 border-opacity-75"
              onClick={restartAnimation}
            >
              Restart Animation
            </button>
            <button
              className="bg-blac rounded-lg px-4 text-zinc-300 text-xs sm:text-base hover:!bg-zinc-200 hover:text-zinc-800 border border-1 border-zinc-700 border-opacity-75"
              onClick={forwardToEnd}
            >
              Forward to the End
            </button>

            <Select onValueChange={(value) => setMapStyle(value)}>
              <SelectTrigger className="sm:w-[220px] w-20 mr-4 text-zinc-300 !bg-[#131313]  text-xs sm:text-base h-10.5 !bg rounded-lg !border-px !border-zinc-700 !border-opacity-75">
                <SelectValue
                  className="text-zinc-300 "
                  placeholder="Select a map style"
                />
              </SelectTrigger>
              <SelectContent className="">
                <SelectGroup>
                  {listOfthemes.map((theme) => (
                    <SelectItem key={theme.value} value={theme.value}>
                      {theme.name}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <a
            href="https://github.com/yourusername/your-repo"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-zinc-5 text-xs sm:text-base rounded-lg px-4 text-zinc-300 hover:!bg-zinc-200 hover:text-zinc-800 border border-1 border-zinc-700 border-opacity-75"
          >
            <svg
              height="24"
              viewBox="0 0 16 16"
              width="24"
              className="fill-current"
            >
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
            </svg>
            <span className="hidden sm:block">View on GitHub</span>
          </a>
        </div>
        <div className="p-4 flex-col">
          <ResizablePanelGroup direction="horizontal">
            <ResizablePanel
              className="pl-4 h-[30vh] sm:h-full rounded-lg overflow-hidden"
              minSize={20}
              defaultSize={70}
            >
              <BaseMap />
            </ResizablePanel>
            <ResizableHandle className="mx-1" />
            <ResizablePanel minSize={20} className="hidden sm:block">
              <div className="flex gap-2 flex-col ml-2  h-[80vh] ">
                <DroneFootageVideo />
                <div
                  ref={parent}
                  className="h-full overflow-y-scroll overflow-x-hidden border-zinc-600"
                >
                  <FoundVehiclesList />
                </div>
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>

          <div className="block sm:hidden ">
            <div className="flex gap-2 flex-col h-[55vh] ">
              <div className=" ml-4 mt-4">
                <DroneFootageVideo />
              </div>
              <div
                ref={parent}
                className="h-full overflow-y-scroll ml-4 overflow-x-hidden border-zinc-600"
              >
                <FoundVehiclesList />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
