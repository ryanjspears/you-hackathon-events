import { useSyncExternalStore } from "react"

const MOBILE_BREAKPOINT = 768
const query = () => window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`)

function subscribe(cb: () => void) {
  const mql = query()
  mql.addEventListener("change", cb)
  return () => mql.removeEventListener("change", cb)
}

export function useIsMobile() {
  return useSyncExternalStore(
    subscribe,
    () => query().matches,
    () => false,
  )
}
