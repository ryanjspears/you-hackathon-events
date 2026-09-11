"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { setUser } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LoginPage() {
  const [name, setName] = useState("");
  const router = useRouter();
  return (
    <div className="mx-auto mt-12 max-w-md sm:mt-24">
      <h1 className="text-[1.75rem] font-semibold leading-tight sm:text-4xl">
        Who&apos;s going out?
      </h1>
      <p className="mt-4 max-w-prose text-muted-foreground">
        Pick a name. Your searches and the events you say you&apos;re going to are remembered under it, so next time the list is already yours.
      </p>
      <form
        className="mt-8 flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          const n = name.trim().toLowerCase();
          if (!n) return;
          setUser(n);
          router.push("/");
        }}
      >
        <Input autoFocus placeholder="Your name" aria-label="Your name" value={name} onChange={(e) => setName(e.target.value)} className="h-11 rounded-full px-4 text-base" />
        <Button type="submit" size="lg" className="h-11 px-5" disabled={!name.trim()}>
          Continue
        </Button>
      </form>
    </div>
  );
}
