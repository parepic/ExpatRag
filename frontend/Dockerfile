FROM node:22-bookworm-slim

ENV PNPM_HOME=/pnpm \
    PATH="/pnpm:$PATH" \
    NEXT_TELEMETRY_DISABLED=1

RUN corepack enable && corepack prepare pnpm@10 --activate

WORKDIR /app/frontend

COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY frontend ./

EXPOSE 3000

CMD ["pnpm", "dev", "--hostname", "0.0.0.0"]
