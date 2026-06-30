interface DeviceQrViewProps {
  status: string | null;
  qr: string | null;
  phone: string | null;
}

/** Presentational QR/status panel shared by the add + connect dialogs. */
export function DeviceQrView({ status, qr, phone }: DeviceQrViewProps) {
  return (
    <div className="flex flex-col items-center gap-3 py-2 text-center">
      {status === "connected" ? (
        <p className="text-sm font-medium text-emerald-600">
          Connected{phone ? ` · ${phone}` : ""}
        </p>
      ) : status === "failed" ? (
        <p className="text-sm font-medium text-destructive">
          Couldn&apos;t start the session — usually low memory. Check the wa-service logs, then
          close and try again.
        </p>
      ) : qr ? (
        <>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={qr} alt="WhatsApp QR code" className="h-56 w-56 rounded-md border" />
          <p className="text-sm text-muted-foreground">
            WhatsApp → Linked devices → Link a device, then scan.
          </p>
        </>
      ) : (
        <p className="text-sm text-muted-foreground">
          Starting session… this can take up to a minute on first launch.
        </p>
      )}
    </div>
  );
}
