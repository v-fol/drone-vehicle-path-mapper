import { foundVehiclesImagesAtom } from "@/atoms";
import PathJson from "@/pathGEO.json";

import { lightenColor } from "@/utils";

import { useAtom, useSetAtom } from "jotai";
import { visibleDataAtom, isAnimatingAtom, selectedVehicleAtom } from "@/atoms";

function FoundVehiclesList() {
  const setVisibleData = useSetAtom(visibleDataAtom);
  const [foundVehiclesImages] = useAtom(foundVehiclesImagesAtom);
  const [isAnimating] = useAtom(isAnimatingAtom);
  const [selectedVehicle, setSelectedVehicle] = useAtom(selectedVehicleAtom);

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

  const showPointsForVehicle = (vehicleId: string) => {
    const features = PathJson.features.filter(
      (feature) => feature.properties.vehicle_id === vehicleId
    );

    // decries the opacity to show the direction of the path
    var index = 0;
    features.forEach((feature) => {
        feature.properties.color = lightenColor(feature.properties.color, index);
        index += 0.15;
    });

    setVisibleData({
      type: "FeatureCollection",
      features: features as GeoJSON.Feature[],
    });
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
              className={`flex justify-between p-2 mt-3 bg-zinc-800 rounded-xl mr-2 ${
                !isAnimating ? "cursor-pointer hover:bg-zinc-700" : ""
              } ${
                selectedVehicle === currentImage.vehicle_id
                  ? "!border-none bg-zinc-600 !border-zinc-500"
                  : ""
              }`}
              style={{
                background:
                  isAnimating ||
                  (!isAnimating && selectedVehicle === currentImage.vehicle_id)
                    ? `linear-gradient(90deg, ${currentImage.color}30 6%, rgba(43, 43, 43, 1) 70%)`
                    : "",
              }}
              onClick={() => {
                !isAnimating && showPointsForVehicle(currentImage.vehicle_id);
                setSelectedVehicle(currentImage.vehicle_id);
              }}
            >
              <div
                className="h-16 w-2 ml-0.5 rounded-md"
                style={{ backgroundColor: `${currentImage.color}` }}
              />
              <span className="text-white mt-5">
                ID: {currentImage.vehicle_id.replace(/\D/g, "")} Confidence{" "}
                {(currentImage.confidence * 100).toFixed(2)}%
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
