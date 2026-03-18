"use client";

import { useState } from "react";
import ISO6391 from "iso-639-1";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const languageNames = new Intl.DisplayNames(["en"], { type: "language" });

const ALL_LANGUAGES = ISO6391.getAllCodes().map((code) => ({
  code,
  name: languageNames.of(code) ?? ISO6391.getName(code),
})).sort((a, b) => (a.name ?? "").localeCompare(b.name ?? ""));

interface LanguageComboboxProps {
  value: string[]; // array of display names
  onChange: (value: string[]) => void;
}

export function LanguageCombobox({ value, onChange }: LanguageComboboxProps) {
  const [open, setOpen] = useState(false);

  function toggle(name: string) {
    if (value.includes(name)) {
      onChange(value.filter((v) => v !== name));
    } else {
      onChange([...value, name]);
    }
  }

  return (
    <div className="flex flex-col gap-3">
      {value.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {value.map((lang) => (
            <Badge key={lang} variant="secondary" className="gap-1">
              {lang}
              <button onClick={() => toggle(lang)} className="ml-1 text-xs">×</button>
            </Badge>
          ))}
        </div>
      )}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            type="button"
            variant="outline"
            className="w-full justify-start text-left font-normal text-muted-foreground"
          >
            {value.length === 0 ? "Search languages…" : "Add another language…"}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-72 p-0">
          <Command>
            <CommandInput placeholder="Search…" />
            <CommandEmpty>No language found.</CommandEmpty>
            <CommandGroup className="max-h-60 overflow-auto">
              {ALL_LANGUAGES.map(({ code, name }) => (
                <CommandItem
                  key={code}
                  value={name ?? code}
                  onSelect={() => { if (name) toggle(name); }}
                >
                  {value.includes(name ?? "") ? "✓ " : ""}{name}
                </CommandItem>
              ))}
            </CommandGroup>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
