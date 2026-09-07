"""
network/packet_capture.py

Live network packet capture module using Scapy.

IMPORTANT NOTES:
----------------
1. Live capture requires ROOT/SUDO privileges on Linux.
   If not available, this module degrades gracefully — the rest
   of the system continues to work with CICIDS2017 dataset samples.

2. This module is for DEMONSTRATION ONLY.
   DO NOT use it to capture traffic on networks you don't own.
   DO NOT transmit captured data outside your local system.

3. For the academic demo, use the dataset-based path instead.
   This module is shown to demonstrate Scapy capability.
"""

import threading
from typing import Callable, Optional


def check_capture_available() -> tuple[bool, str]:
    """
    Check if live packet capture is possible on this system.

    Returns:
        (available: bool, reason: str)
    """
    try:
        import scapy.all as scapy
    except ImportError:
        return False, "Scapy is not installed"

    import os
    if os.name == "nt":
        # Windows requires WinPcap/Npcap
        try:
            scapy.conf.use_pcap = True
            return True, "Windows capture available (Npcap required)"
        except Exception as e:
            return False, f"Windows capture unavailable: {e}"

    # Linux/macOS: check for root privileges
    if os.geteuid() != 0:
        return False, (
            "Root privileges required for live capture on Linux/macOS. "
            "Run with: sudo python network/packet_capture.py "
            "(Not required for dataset-based demo)"
        )

    return True, "Live capture available"


def capture_packets(
    interface: Optional[str] = None,
    count: int = 100,
    timeout: int = 10,
    filter_expr: str = "ip",
    callback: Optional[Callable] = None,
) -> list:
    """
    Capture live packets from a network interface.

    Args:
        interface:   Network interface (e.g., 'eth0', 'wlan0').
                     None = Scapy picks the default interface.
        count:       Number of packets to capture (0 = unlimited)
        timeout:     Stop after this many seconds
        filter_expr: BPF filter (e.g., 'tcp port 80')
        callback:    Optional per-packet callback function

    Returns:
        List of Scapy packet objects

    Raises:
        PermissionError: if not running as root
        RuntimeError:    if Scapy is unavailable or capture fails
    """
    available, reason = check_capture_available()
    if not available:
        raise PermissionError(
            f"Cannot capture packets: {reason}\n"
            "Use dataset-based inference instead: "
            "the system works fully without live capture."
        )

    try:
        import scapy.all as scapy
        print(f"[CAPTURE] Starting capture on interface: {interface or 'default'}")
        print(f"[CAPTURE] Filter: '{filter_expr}' | Count: {count} | Timeout: {timeout}s")

        packets = scapy.sniff(
            iface=interface,
            count=count,
            timeout=timeout,
            filter=filter_expr,
            prn=callback,
            store=True,
        )

        print(f"[CAPTURE] Captured {len(packets)} packets")
        return list(packets)

    except Exception as e:
        raise RuntimeError(f"Packet capture failed: {type(e).__name__}: {e}")


def get_available_interfaces() -> list[str]:
    """Return list of available network interfaces."""
    try:
        import scapy.all as scapy
        return scapy.get_if_list()
    except Exception:
        return []


class ContinuousCapture:
    """
    Background packet capture with flow accumulation.

    Captures packets in a background thread and processes them
    in configurable flow windows.

    Usage:
        capture = ContinuousCapture(on_flow_callback=my_handler)
        capture.start()
        ...
        capture.stop()
    """

    def __init__(
        self,
        interface: Optional[str] = None,
        window_size: int = 50,       # Packets per flow window
        on_flow_callback: Optional[Callable] = None,
    ):
        self.interface = interface
        self.window_size = window_size
        self.on_flow_callback = on_flow_callback
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._packet_buffer = []
        self._buffer_lock = threading.Lock()

    def start(self):
        """Start background capture."""
        available, reason = check_capture_available()
        if not available:
            print(f"[CAPTURE] Live capture unavailable: {reason}")
            print("[CAPTURE] Using dataset-based simulation instead.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._capture_loop, daemon=True, name="ai-snids-capture"
        )
        self._thread.start()
        print("[CAPTURE] Background capture started.")

    def stop(self):
        """Stop background capture."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        print("[CAPTURE] Background capture stopped.")

    def _capture_loop(self):
        """Internal capture loop — runs in background thread."""
        try:
            import scapy.all as scapy

            def process_packet(pkt):
                if self._stop_event.is_set():
                    return
                with self._buffer_lock:
                    self._packet_buffer.append(pkt)
                    if len(self._packet_buffer) >= self.window_size:
                        flow_packets = self._packet_buffer[: self.window_size]
                        self._packet_buffer = self._packet_buffer[self.window_size:]
                        if self.on_flow_callback:
                            self.on_flow_callback(flow_packets)

            scapy.sniff(
                iface=self.interface,
                filter="ip",
                prn=process_packet,
                stop_filter=lambda _: self._stop_event.is_set(),
                store=False,
            )
        except Exception as e:
            print(f"[CAPTURE] Error in capture loop: {e}")
