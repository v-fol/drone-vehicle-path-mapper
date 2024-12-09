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
      {[...foundVehiclesImages].reverse().map((image, index) => {
        if (index == foundVehiclesImages.length - 1) {
          return <span key={index}></span>;
        } else {
          return (
            <div key={index} className="flex justify-between p-2">
                <div className="h-16 w-2 rounded-md" style={{backgroundColor: image.color}}/>
                <span className="text-white mt-2">ID: {image.vehicle_id.replace(/\D/g, '')} Confidence {image.confidence * 100}%</span>
              <img
                className="h-16  rounded-md"
                src={getImageUrl(image.vehicle_id)}
                alt={`Vehicle ${image.vehicle_id}`}
              />
            </div>
          );
        }
      })}
    </>
  );
}

export default FoundVehiclesList;
