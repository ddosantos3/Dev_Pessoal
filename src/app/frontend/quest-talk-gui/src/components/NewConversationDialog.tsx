import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

interface NewConversationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreate: (context: string) => void;
}

export function NewConversationDialog({
  open,
  onOpenChange,
  onCreate,
}: NewConversationDialogProps) {
  const [context, setContext] = useState("");

  useEffect(() => {
    if (!open) {
      setContext("");
    }
  }, [open]);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onCreate(context.trim());
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <form onSubmit={handleSubmit} className="space-y-5">
          <DialogHeader>
            <DialogTitle>Nova conversa</DialogTitle>
            <DialogDescription>
              Defina um contexto ou descrição para esta conversa. Isso ajuda o agente a entender
              sobre o que vocês estão falando e será usado como título no histórico.
            </DialogDescription>
          </DialogHeader>

          <Textarea
            value={context}
            onChange={(event) => setContext(event.target.value)}
            placeholder="Ex.: Landing page para barbearia boutique com foco premium."
            rows={4}
            className="rounded-2xl border border-slate-200 bg-slate-50 text-slate-800 placeholder:text-slate-400 focus-visible:ring-slate-300"
          />

          <DialogFooter className="gap-2 sm:gap-0">
            <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit">Iniciar conversa</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
