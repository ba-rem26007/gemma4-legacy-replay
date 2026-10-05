# Topic 745818: CuriosIT: Autonomous Bare-Metal Diagnostics with Gemma 4 on Android (100% Offline & Air-Gapped)

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745818
- **Date** : 2026-10-04T15:44:31.602000
- **Votes** : 0 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-04T15:44:31.603000) [Votes: 0]

The competition prompt poses a great question: 



  "What if every developer could rely on an autonomous agent equally capable offline, on consumer hardware?"



We took this challenge directly to bare-metal hardware and End User Computing (EUC) field diagnostics. 


Meet CuriosIT — an autonomous hardware-assisted diagnostic copilot that operates 100% offline with zero cloud data exfiltration.






### 🛠️ The Architecture


- Neural Core: Google Gemma 4B running 100% locally on a mobile device (Google Pixel) using Google LiteRT-LM with INT4 quantization on the Tensor NPU/GPU.

- Physical Hardware Bridge: A compact ESP32-S3 USB dongle running custom dual-mode firmware (simultaneous USB HID keystroke injection + CDC virtual serial loopback) with hardware SPI telemetry on an IPS LCD.

- Air-Gap Compliance: The target machine (which may be broken, offline, or in a restricted environment like healthcare/finance) has NO internet connection. All telemetry streams locally over an encrypted BLE NUS link to the phone.




### ⚡ Live Field Test Example

During a live terminal troubleshooting session on a bare-metal Linux host:



- The technician asked Gemma on the phone: "i need to find all attached usb".

- Gemma reasoned locally on GPU and prepared the diagnostic action: `[ ⚡ INJECT TO PC: lsusb ]`.

- With a single tap, the dongle typed `(lsusb) 2>&1 | tee /dev/ttyACM0` into the host bash terminal and streamed the raw bus output back to the phone.

Next prompt from technician: "whats for keyboard?"


](url to embed)



- Gemma on GPU response:



  "Sorted mate, you've got a Corsair K55 CORE RGB Gaming Keyboard attached there."



No cloud calls, no external API keys, sub-second reasoning, and accurate hardware identification at the physical terminal!




### 💡 Why This Matters for Autonomous Agents


- Democratizing Enterprise IT: A $20 USB dongle and a consumer mobile phone replace a bulky $2,500 rugged technician workstation.

- Strict Air-Gap Safety: Ideal for hospitals (NHS), defense, and banking where uploading system logs or internal network topologies to public cloud LLMs is strictly prohibited.

- Enterprise MCP Ready: Architected to link with Active Directory (LAPS) and PDQ Deploy via Model Context Protocol.


We'd love to hear your thoughts, feedback, and ideas from the DeepMind team and the community!

---
