import React from "react";
import BaseMap from "@/components/BaseMap";
import FoundVehiclesList from "@/components/FoundVehiclesList";
import video from "@/assets/video.mp4";
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

  const [mapStyle, setMapStyle] = useAtom(mapStyleAtom);

  const restartAnimation = () => {
    setVisibleData({ type: "FeatureCollection", features: [] });
    setCurrentIndex(0);
    setFoundVehiclesImages([]);

    // this is so that the video will restart
    setIsAnimating(false);
    setTimeout(() => {
      setIsAnimating(true);
    }, 200);
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
      <div className=" bg-zinc-900 h-[100vh]">
        <div className="px-4 pt-4 flex gap-4 ">
          <button
            className="bg-black rounded-lg px-4 text-zinc-300 text-md hover:!bg-zinc-200 hover:text-zinc-800 border border-1 border-zinc-700"
            onClick={restartAnimation}
          >
            Restart Animation
          </button>
          <button
            className="bg-black rounded-lg px-4 text-zinc-300 text-md hover:!bg-zinc-200 hover:text-zinc-800 border border-1 border-zinc-700"
            onClick={forwardToEnd}
          >
            Forward to the End
          </button>
          <Select onValueChange={(value) => setMapStyle(value)}>
            <SelectTrigger className="w-[280px] text-zinc-300 text-md h-10.5 !bg rounded-lg !border-1 !border-zinc-700">
              <SelectValue
                className="text-zinc-300"
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
        <div className="p-4">
          <ResizablePanelGroup direction="horizontal">
            <ResizablePanel minSize={20} defaultSize={70}>
              <BaseMap />
            </ResizablePanel>
            <ResizableHandle />
            <ResizablePanel minSize={20}>
              <div className="flex gap-4 flex-col ml-2  h-[80vh] ">
                {isAnimating ? (
                  <div className="w-full  bg-zinc-800 rounded-xl relative">
                    <video src={video} autoPlay muted className="rounded-xl " />
                  </div>
                ) : (
                  // show the video but pause it
                  <div className="w-full  bg-zinc-800 rounded-xl relative">
                    <span className="text-white  text-2xl absolute left-0 right-0 m-auto w-fit top-0 bottom-0 h-fit opacity-40">
                      Resume animation to continue
                    </span>
                    <video
                      src={video}
                      style={{ opacity: 0.2 }}
                      className="w-full h-62 rounded-xl"
                    />
                  </div>
                )}

                <div
                  ref={parent}
                  className="h-full overflow-y-scroll overflow-x-hidden border-zinc-600"
                >
                  <FoundVehiclesList />
                </div>
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </div>
      </div>
    </>
  );
}
