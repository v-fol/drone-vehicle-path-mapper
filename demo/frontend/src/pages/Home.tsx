import React from "react";
import BaseMap from "@/components/BaseMap";
import FoundVehiclesList from "@/components/FoundVehiclesList";
import video from "@/assets/video.mp4";
import PathJson from "@/pathGEO.json";

import { Button } from "@/components/ui/button";

import { useAtom } from "jotai";
import { isAnimatingAtom, visibleDataAtom, currentIndexAtom, foundVehiclesImagesAtom } from "@/atoms";

export default function Home() {
  const [isAnimating, setIsAnimating] = useAtom(isAnimatingAtom);
  const [visibleData, setVisibleData] = useAtom(visibleDataAtom);
  const [currentIndex, setCurrentIndex] = useAtom(currentIndexAtom);
    const [foundVehiclesImages, setFoundVehiclesImages] = useAtom(foundVehiclesImagesAtom);

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
            (vehicle) => vehicle.vehicle_id === PathJson.features[i].properties.vehicle_id
        );
        if (!found){
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
      <div className=" bg-zinc-800">
        <div>
          <Button onClick={restartAnimation}>Restart Animation</Button>
          <Button onClick={forwardToEnd}>Forward to End</Button>
        </div>
        <div className="flex gap-4  p-4">
          <div className="">
            <BaseMap />
          </div>
          <div className="flex gap-4 flex-col   h-[90vh]">
            <div>
              {isAnimating ? (
                <div className="w-full  bg-zinc-800 rounded-xl relative">
                  <video src={video} autoPlay muted className="rounded-xl " />
                </div>
              ) : (
                // show the video but pause it
                <div className="w-full  bg-zinc-800 rounded-xl relative">
                  <span className="text-white text-3xl absolute left-0 right-0 m-auto w-fit top-0 bottom-0 h-fit opacity-40">
                    Resume animation to continue
                  </span>
                  <video
                    src={video}
                    style={{ opacity: 0.2 }}
                    className="w-full h-62 rounded-xl"
                  />
                </div>
              )}
            </div>
            <div className="h-full  overflow-y-auto   border-zinc-600 ">
              <FoundVehiclesList />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
