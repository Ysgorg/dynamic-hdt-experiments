#syntax=docker/dockerfile:1.3@sha256:93f32bd6dd9004897fed4703191f48924975081860667932a4df35ba567d7426

ARG CACHE_BUST

FROM registry.triply.cc/triply/hdt/dynamic-hdt:latest as final
RUN mkdir /root/dynamic-benchmark
COPY ./bin /root/dynamic-benchmark/scripts 
COPY ./configs /root/dynamic-benchmark/configs
RUN apt-get install -y pwgen time