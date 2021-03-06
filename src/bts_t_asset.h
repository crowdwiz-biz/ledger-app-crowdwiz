/*******************************************************************************
*  Copyright of the Contributing Authors, including:
*
*   (c) 2019 Christopher J. Sanborn
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      http://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License.
********************************************************************************/

#ifndef __BTS_T_ASSET_H__
#define __BTS_T_ASSET_H__

#include <stdbool.h>
#include "os.h"

typedef struct bts_asset_type_t {
    uint64_t     amount;
    uint64_t     instanceId;
} bts_asset_type_t;

typedef struct bts_asset_description_t {
    uint8_t precision;
    char    symbol[23]; // More than enough to accomodate longest symbol or
                        // '[1.3.xxx]' for largest instanceId
} bts_asset_description_t;

uint32_t deserializeBtsAssetType(const uint8_t *buffer, uint32_t bufferLength, bts_asset_type_t * asset);

uint32_t prettyPrintBtsAssetType(bts_asset_type_t asset, char * buffer);

bool getBtsAssetDescription(bts_asset_type_t asset, bts_asset_description_t *desc);

#endif
