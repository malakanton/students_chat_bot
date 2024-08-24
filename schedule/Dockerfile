FROM golang:1.22.1-alpine AS builder

WORKDIR /schedule

RUN apk --no-cache add bash git make gcc gettext musl-dev tzdata

COPY ["./go.mod", "./go.sum", "./"]
RUN go mod download

COPY . ./
RUN go build -o ./bin/app ./cmd/schedule/main.go

FROM alpine AS runner

COPY --from=builder /schedule/bin/app /
COPY config/dev.yaml /dev.yaml
COPY /internal/gglapi/studentsbot-414221-88a1d65d3976.json /studentsbot-414221-88a1d65d3976.json

EXPOSE 8080

ENV CONFIG_PATH=/dev.yaml

CMD ["/app"]
