import React from "react";
import video from "../assets/video.mp4";

import { useAtom } from "jotai";
import { isAnimatingAtom, foundVehiclesImagesAtom } from "@/atoms";

// import { useRef } from 'react'
import { useAutoAnimate } from "@formkit/auto-animate/react";

function DroneFootageVideo() {
  const [isAnimating] = useAtom(isAnimatingAtom);
  const [foundVehiclesImages] = useAtom(foundVehiclesImagesAtom);
  const [parent, enableAnimations] = useAutoAnimate();

  return (
    <>
      <div className="mr-4">
        {isAnimating ? (
          <div className="w-full  bg-zinc-800 rounded-xl relative">
            <video src={video} autoPlay muted className="rounded-xl " />
          </div>
        ) : (
          // show the video but pause it
          <div className="w-full  bg-zinc-800 rounded-xl relative">
            <span className="text-white  text-2xl absolute left-0 right-0 m-auto w-fit top-0 bottom-0 h-fit opacity-40">
              Restart animation to continue
            </span>
            <video
              src={video}
              style={{ opacity: 0.2 }}
              className="w-full h-62 rounded-xl"
            />
          </div>
        )}
      </div>
      <div ref={parent} className="translate-y-2">
        {foundVehiclesImages.length > 0 && !isAnimating && (
          <div className="bg-yellow-950/30 text-yellow-300/90 text-sm px-2 py-2 border border-yellow-600/30 border-dashed rounded-lg flex items-center justify-center gap-2 mr-4">
            💡 Click on the vehicles below to see their individual paths
          </div>
        )}
      </div>
    </>
  );
}

export default DroneFootageVideo;
