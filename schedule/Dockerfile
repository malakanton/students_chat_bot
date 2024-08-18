FROM golang:1.22.1-alpine AS builder

WORKDIR /schedule

RUN apk --no-cache add bash git make gcc gettext musl-dev

COPY ["./go.mod", "./go.sum", "./"]
RUN go mod download

COPY . ./
RUN go build -o ./bin/app ./cmd/schedule/main.go

FROM alpine AS runner

COPY --from=builder /schedule/bin/app /
COPY config/dev.yaml /dev.yaml

ENV CONFIG_PATH=/dev.yaml

CMD ["/app"]
