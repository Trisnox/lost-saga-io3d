---
title: Shader Operator
order: 8
---

## Turn Material into Opaque
Turn selected object material into opaque.

What this actually does are:

- Set opacity to 0%
- Uncheck `Invert` box
- Uncheck `Invert Transparency` box

## Turn Material into Transparent
Turn selected object material into transparent. This will turn any black colored pixel to transparent.

What this actually does are:

- Set opacity to 0%
- Check `Forced Transparency` box

## Toggle Shadeless
Toggle selected object material into shaded/shadeless.

What this actually does are:

If emission strength is at 100% or more:

- Set the emission strength to 0%
 
If emission strength is less than 100%:

- Set the emission strength to 100%
- Check `Preserve Color` box