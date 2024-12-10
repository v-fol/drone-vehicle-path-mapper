import React from "react";
import { useAtom } from "jotai";
import { foundVehiclesImagesAtom } from "@/atoms";

function FoundVehiclesList() {
  const [foundVehiclesImages] = useAtom(foundVehiclesImagesAtom);

  // Helper function to dynamically import images
  const getImageUrl = (vehicleId: string) => {
    try {
      // Using dynamic import for images
      return new URL(`../assets/car/${vehicleId}.jpg`, import.meta.url).href;
    } catch (error) {
      console.error(`Error loading image for vehicle ${vehicleId}:`, error);
      return ""; // or a fallback image URL
    }
  };

  return (
    <>
      {[...foundVehiclesImages].map((_, index) => {
        const reverseIndex = foundVehiclesImages.length - 1 - index; // Reverse the rendering order
        const currentImage = foundVehiclesImages[reverseIndex];
        if (reverseIndex === 0) {
          return <span key={reverseIndex}></span>;
        } else {
          return (
            <div
              key={reverseIndex}
              className="flex justify-between p-2 bg-zinc-800 rounded-xl mt-3 "
            >
              <div
                className="h-16 w-2 rounded-md"
                style={{ backgroundColor: currentImage.color }}
              />
              <span className="text-white mt-5">
                ID: {currentImage.vehicle_id.replace(/\D/g, "")} Confidence{" "}
                {currentImage.confidence * 100}%
              </span>
              <img
                className="h-16 rounded-md"
                src={getImageUrl(currentImage.vehicle_id)}
                alt={`Vehicle ${currentImage.vehicle_id}`}
              />
            </div>
          );
        }
      })}
    </>
  );
}

export default FoundVehiclesList;
