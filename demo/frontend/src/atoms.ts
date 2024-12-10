import { atom } from 'jotai'
import { Vehicle } from '@/types/global'

export const isAnimatingAtom = atom<boolean>(false)

export const foundVehiclesImagesAtom = atom<Vehicle[]>([])

export const currentIndexAtom = atom<number>(0)

export const visibleDataAtom = atom<GeoJSON.FeatureCollection>({
  type: 'FeatureCollection',
  features: [],
})

export const mapStyleAtom = atom<string>('mapbox://styles/mapbox/dark-v11')